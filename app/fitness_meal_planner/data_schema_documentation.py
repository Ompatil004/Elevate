"""
Data Schema Documentation for Fitness and Meal Planner
Ethical and realistic dataset design

This document outlines the data schema for collecting user information
in a way that is ethical, privacy-preserving, and focused on user experience
rather than diagnostic measurements.
"""

# USER PROFILE DATA SCHEMA
USER_PROFILE_SCHEMA = {
    "user_id": {
        "type": "string (UUID)",
        "description": "Unique anonymous identifier for the user",
        "ethics_note": "Never correlates to real identity, hashed when stored long-term"
    },
    "timestamp": {
        "type": "ISO 8601 string",
        "description": "When the profile was created/updated"
    },
    "age": {
        "type": "integer",
        "range": "13-100",
        "description": "User-reported age (not verified)",
        "ethics_note": "Represents user's self-identification, not medical verification"
    },
    "weight": {
        "type": "float",
        "unit": "kilograms",
        "range": "20-300",
        "description": "User-reported weight (not measured by system)",
        "ethics_note": "Self-reported value, not diagnostic measurement"
    },
    "height": {
        "type": "float", 
        "unit": "centimeters",
        "range": "50-250",
        "description": "User-reported height (not measured by system)",
        "ethics_note": "Self-reported value, not diagnostic measurement"
    },
    "gender": {
        "type": "string",
        "options": ["male", "female", "non-binary", "prefer_not_to_say", "other"],
        "description": "User's self-identified gender"
    },
    "fitness_goal": {
        "type": "string",
        "options": [
            "fat_loss", "muscle_gain", "maintenance", 
            "general_fitness", "endurance", "strength"
        ],
        "description": "User's stated fitness goal (not evaluated for 'appropriateness')"
    },
    "experience_level": {
        "type": "string",
        "options": ["beginner", "intermediate", "advanced"],
        "description": "User's self-assessed experience level"
    },
    "equipment_available": {
        "type": "array of strings",
        "description": "Equipment user reports having access to",
        "examples": ["dumbbells", "yoga_mat", "resistance_bands", "none"]
    },
    "dietary_preference": {
        "type": "string",
        "description": "User's stated dietary preferences",
        "examples": ["vegetarian", "vegan", "pescatarian", "omnivore", "gluten_free", "dairy_free"]
    },
    "allergies_or_constraints": {
        "type": "array of strings",
        "description": "User-reported allergies or dietary constraints (not medically verified)",
        "examples": ["nuts", "dairy", "gluten", "shellfish"],
        "ethics_note": "User-reported information, system filters accordingly but doesn't diagnose"
    },
    "disclaimer_acknowledged": {
        "type": "boolean",
        "description": "Whether user acknowledged system is not medical advice"
    },
    "consent_given": {
        "type": "boolean", 
        "description": "Whether user consented to data collection"
    }
}

# WORKOUT BEHAVIOR DATA SCHEMA
WORKOUT_BEHAVIOR_SCHEMA = {
    "record_id": {
        "type": "string (UUID)",
        "description": "Unique identifier for this behavior record"
    },
    "user_id": {
        "type": "string (UUID)",
        "description": "Reference to user profile"
    },
    "timestamp": {
        "type": "ISO 8601 string",
        "description": "When the behavior was recorded"
    },
    "workout_id": {
        "type": "string",
        "description": "Identifier for the specific workout"
    },
    "completion_status": {
        "type": "string",
        "options": ["completed", "partially_completed", "skipped", "interrupted"],
        "description": "User-reported workout completion status",
        "ethics_note": "Represents user's experience, not 'correctness'"
    },
    "perceived_difficulty": {
        "type": "string",
        "options": ["easy", "moderate", "hard"],
        "description": "How difficult the user found the workout",
        "ethics_note": "Subjective user experience, not objective difficulty"
    },
    "fatigue_level": {
        "type": "string",
        "options": ["low", "medium", "high", "unknown"],
        "description": "User's reported fatigue level after workout",
        "ethics_note": "Subjective experience, not physiological measurement"
    },
    "recovery_duration": {
        "type": "string", 
        "options": ["short", "average", "long", "unknown"],
        "description": "User's perceived recovery time needed",
        "ethics_note": "Subjective perception, not medical assessment"
    },
    "notes": {
        "type": "string",
        "description": "User's free-form notes about the workout experience"
    },
    "user_experience_feedback": {
        "type": "string",
        "description": "User's qualitative feedback about their experience"
    }
}

# MEAL BEHAVIOR DATA SCHEMA
MEAL_BEHAVIOR_SCHEMA = {
    "record_id": {
        "type": "string (UUID)",
        "description": "Unique identifier for this behavior record"
    },
    "user_id": {
        "type": "string (UUID)", 
        "description": "Reference to user profile"
    },
    "timestamp": {
        "type": "ISO 8601 string",
        "description": "When the behavior was recorded"
    },
    "meal_id": {
        "type": "string",
        "description": "Identifier for the specific meal"
    },
    "adherence_level": {
        "type": "string",
        "options": ["followed", "partial", "skipped"],
        "description": "How closely user followed the meal plan",
        "ethics_note": "User-reported adherence, not nutritional correctness"
    },
    "enjoyment_rating": {
        "type": "string",
        "options": ["low", "medium", "high", "unknown"],
        "description": "User's enjoyment of the meal",
        "ethics_note": "Subjective experience, not nutritional value"
    },
    "satisfaction_level": {
        "type": "string",
        "options": ["unsatisfied", "neutral", "satisfied", "very_satisfied", "unknown"],
        "description": "How satisfied the user was with the meal",
        "ethics_note": "Subjective experience, not nutritional adequacy"
    },
    "hunger_level_after": {
        "type": "string",
        "options": ["very_hungry", "hungry", "neutral", "satisfied", "full", "very_full", "unknown"],
        "description": "User's hunger level after eating",
        "ethics_note": "Subjective feeling, not metabolic state"
    },
    "notes": {
        "type": "string",
        "description": "User's free-form notes about the meal experience"
    },
    "user_experience_feedback": {
        "type": "string",
        "description": "User's qualitative feedback about their meal experience"
    }
}

# ETHICAL PRINCIPLES GUIDING DATA COLLECTION

ETHICAL_PRINCIPLES = {
    "user_consent": {
        "principle": "Explicit consent required",
        "implementation": "Users must actively consent before data collection begins"
    },
    "data_minimization": {
        "principle": "Collect only necessary data",
        "implementation": "Only collect data that directly improves user experience"
    },
    "no_diagnostic_claims": {
        "principle": "Do not make medical or diagnostic claims",
        "implementation": "All data represents user experience, not medical truth"
    },
    "privacy_protection": {
        "principle": "Protect user privacy",
        "implementation": "Anonymize data when possible, secure storage required"
    },
    "user_control": {
        "principle": "Users control their data",
        "implementation": "Allow users to view, modify, and delete their data"
    },
    "transparent_purposes": {
        "principle": "Clear data usage explanation",
        "implementation": "Inform users exactly how their data will be used"
    },
    "avoid_bias": {
        "principle": "Avoid reinforcing harmful biases",
        "implementation": "Design data collection to be inclusive and fair"
    },
    "no_optimal_labels": {
        "principle": "Avoid 'optimal' or 'perfect' classifications",
        "implementation": "Focus on user experience rather than correctness"
    }
}

# PRIVACY AND ANONYMIZATION STRATEGIES

PRIVACY_STRATEGIES = {
    "identifier_anonymization": {
        "method": "Hashing with salt",
        "purpose": "Convert user IDs to irreversible hashes"
    },
    "aggregation_before_analysis": {
        "method": "Group data before analysis",
        "purpose": "Prevent identification of individuals in analytics"
    },
    "data_retention_policy": {
        "method": "Automatic deletion after timeframe",
        "purpose": "Minimize data exposure over time"
    },
    "access_controls": {
        "method": "Role-based access with audit logs",
        "purpose": "Limit who can access personal data"
    },
    "encryption_at_rest": {
        "method": "Strong encryption for stored data",
        "purpose": "Protect data from unauthorized access"
    }
}

# EXAMPLE VALID DATA RECORDS

EXAMPLE_USER_PROFILE = {
    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "timestamp": "2026-02-03T10:30:00Z",
    "age": 28,
    "weight": 68.5,
    "height": 165.0,
    "gender": "female",
    "fitness_goal": "general_fitness",
    "experience_level": "intermediate",
    "equipment_available": ["resistance_bands", "yoga_mat"],
    "dietary_preference": "vegetarian",
    "allergies_or_constraints": ["nuts"],
    "disclaimer_acknowledged": True,
    "consent_given": True
}

EXAMPLE_WORKOUT_BEHAVIOR = {
    "record_id": "f0e9d8c7-a6b5-4321-fedc-ba9876543210",
    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "timestamp": "2026-02-03T18:15:00Z",
    "workout_id": "strength_workout_001",
    "completion_status": "completed",
    "perceived_difficulty": "moderate",
    "fatigue_level": "medium",
    "recovery_duration": "average",
    "notes": "Felt good today, energy levels appropriate",
    "user_experience_feedback": "Liked the exercise selection, good challenge level"
}

EXAMPLE_MEAL_BEHAVIOR = {
    "record_id": "z9y8x7w6-v5u4-3210-t9s8-r7q6p5o4n3m2",
    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "timestamp": "2026-02-03T13:45:00Z",
    "meal_id": "lunch_salad_001",
    "adherence_level": "followed",
    "enjoyment_rating": "high",
    "satisfaction_level": "satisfied",
    "hunger_level_after": "satisfied",
    "notes": "Really enjoyed the flavors and textures",
    "user_experience_feedback": "Will definitely make this again, satisfying but not heavy"
}

if __name__ == "__main__":
    print("Data Schema Documentation for Fitness and Meal Planner")
    print("=" * 60)
    print("\nETHICAL PRINCIPLES:")
    for name, details in ETHICAL_PRINCIPLES.items():
        print(f"  {name.replace('_', ' ').title()}: {details['principle']}")
    
    print(f"\nUSER PROFILE SCHEMA FIELDS: {len(USER_PROFILE_SCHEMA)}")
    print(f"WORKOUT BEHAVIOR SCHEMA FIELDS: {len(WORKOUT_BEHAVIOR_SCHEMA)}")
    print(f"MEAL BEHAVIOR SCHEMA FIELDS: {len(MEAL_BEHAVIOR_SCHEMA)}")
    
    print("\nPRIVACY STRATEGIES IMPLEMENTED:")
    for strategy, details in PRIVACY_STRATEGIES.items():
        print(f"  {strategy.replace('_', ' ').title()}: {details['purpose']}")
    
    print("\nSchema documentation complete. All data represents user experience,")
    print("not diagnostic measurements, with ethical safeguards in place.")