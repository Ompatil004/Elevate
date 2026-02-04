"""
Data Collection Pipeline for Fitness and Meal Planner
Ethical and realistic dataset design
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import os


class FitnessGoal(Enum):
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    GENERAL_FITNESS = "general_fitness"
    ENDURANCE = "endurance"
    STRENGTH = "strength"


class ExperienceLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class DifficultyRating(Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"


class FatigueLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecoveryDuration(Enum):
    SHORT = "short"  # Less than 24 hours
    AVERAGE = "average"  # 24-48 hours
    LONG = "long"  # More than 48 hours


class MealAdherence(Enum):
    FOLLOWED = "followed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class UserDataCollection:
    """
    Class to handle user profile data collection
    All data represents user-reported experiences, not diagnostic measurements
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.user_profiles_file = os.path.join(data_dir, "user_profiles.json")
        self.behavioral_data_file = os.path.join(data_dir, "behavioral_data.json")
        self._ensure_data_dirs_exist()
    
    def _ensure_data_dirs_exist(self):
        """Ensure data directories exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Initialize files if they don't exist
        for file_path in [self.user_profiles_file, self.behavioral_data_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def collect_user_profile(self, profile_data: Dict[str, Any]) -> str:
        """
        Collect user profile data with ethical considerations
        """
        # Validate required fields
        required_fields = ['age', 'weight', 'height', 'gender', 'fitness_goal', 'experience_level']
        for field in required_fields:
            if field not in profile_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create user profile with ethical safeguards
        user_profile = {
            "user_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "age": profile_data["age"],
            "weight": profile_data["weight"],  # User-reported, not measured
            "height": profile_data["height"],  # User-reported, not measured
            "gender": profile_data["gender"],
            "fitness_goal": profile_data["fitness_goal"],
            "experience_level": profile_data["experience_level"],
            "equipment_available": profile_data.get("equipment_available", []),
            "dietary_preference": profile_data.get("dietary_preference", ""),
            "allergies_or_constraints": profile_data.get("allergies_or_constraints", []),
            "disclaimer_acknowledged": profile_data.get("disclaimer_acknowledged", False),
            "consent_given": profile_data.get("consent_given", False)
        }
        
        # Append to user profiles
        profiles = self._load_json_file(self.user_profiles_file)
        profiles.append(user_profile)
        self._save_json_file(self.user_profiles_file, profiles)
        
        return user_profile["user_id"]
    
    def collect_workout_behavior(self, user_id: str, workout_data: Dict[str, Any]) -> str:
        """
        Collect behavioral data related to workouts
        Data represents user experience, not correctness
        """
        required_fields = ['workout_id', 'completion_status', 'perceived_difficulty']
        for field in required_fields:
            if field not in workout_data:
                raise ValueError(f"Missing required field: {field}")
        
        behavior_record = {
            "record_id": str(uuid.uuid4()),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "workout_id": workout_data["workout_id"],
            "completion_status": workout_data["completion_status"],  # User-reported
            "perceived_difficulty": workout_data["perceived_difficulty"],  # User experience
            "fatigue_level": workout_data.get("fatigue_level", "unknown"),
            "recovery_duration": workout_data.get("recovery_duration", "unknown"),
            "notes": workout_data.get("notes", ""),
            "user_experience_feedback": workout_data.get("user_experience_feedback", "")
        }
        
        # Append to behavioral data
        behaviors = self._load_json_file(self.behavioral_data_file)
        behaviors.append(behavior_record)
        self._save_json_file(self.behavioral_data_file, behaviors)
        
        return behavior_record["record_id"]
    
    def collect_meal_behavior(self, user_id: str, meal_data: Dict[str, Any]) -> str:
        """
        Collect behavioral data related to meals
        Data represents user experience, not nutritional correctness
        """
        required_fields = ['meal_id', 'adherence_level']
        for field in required_fields:
            if field not in meal_data:
                raise ValueError(f"Missing required field: {field}")
        
        behavior_record = {
            "record_id": str(uuid.uuid4()),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "meal_id": meal_data["meal_id"],
            "adherence_level": meal_data["adherence_level"],  # User-reported adherence
            "enjoyment_rating": meal_data.get("enjoyment_rating", "unknown"),
            "satisfaction_level": meal_data.get("satisfaction_level", "unknown"),
            "hunger_level_after": meal_data.get("hunger_level_after", "unknown"),
            "notes": meal_data.get("notes", ""),
            "user_experience_feedback": meal_data.get("user_experience_feedback", "")
        }
        
        # Append to behavioral data
        behaviors = self._load_json_file(self.behavioral_data_file)
        behaviors.append(behavior_record)
        self._save_json_file(self.behavioral_data_file, behaviors)
        
        return behavior_record["record_id"]
    
    def _load_json_file(self, file_path: str) -> List[Dict]:
        """Load JSON data from file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _save_json_file(self, file_path: str, data: List[Dict]):
        """Save JSON data to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


class DataValidation:
    """
    Class to validate collected data for ethical and realistic constraints
    """
    
    @staticmethod
    def validate_user_profile(profile: Dict[str, Any]) -> List[str]:
        """
        Validate user profile data for ethical constraints
        Returns list of validation errors
        """
        errors = []
        
        # Age validation (realistic range)
        age = profile.get('age', -1)
        if not (13 <= age <= 100):
            errors.append("Age must be between 13 and 100")
        
        # Weight validation (realistic range, user-reported)
        weight = profile.get('weight', -1)
        if not (20 <= weight <= 300):  # kg
            errors.append("Weight should be between 20 and 300 kg")
        
        # Height validation (realistic range, user-reported)
        height = profile.get('height', -1)
        if not (50 <= height <= 250):  # cm
            errors.append("Height should be between 50 and 250 cm")
        
        # Validate enums
        if profile.get('fitness_goal') not in [goal.value for goal in FitnessGoal]:
            errors.append("Invalid fitness goal")
        
        if profile.get('experience_level') not in [level.value for level in ExperienceLevel]:
            errors.append("Invalid experience level")
        
        return errors
    
    @staticmethod
    def validate_workout_behavior(behavior: Dict[str, Any]) -> List[str]:
        """
        Validate workout behavior data
        """
        errors = []
        
        if behavior.get('perceived_difficulty') not in [diff.value for diff in DifficultyRating]:
            errors.append("Invalid perceived difficulty rating")
        
        if behavior.get('fatigue_level') not in [fat.value for fat in FatigueLevel] + ['unknown']:
            errors.append("Invalid fatigue level")
        
        if behavior.get('recovery_duration') not in [rec.value for rec in RecoveryDuration] + ['unknown']:
            errors.append("Invalid recovery duration")
        
        return errors
    
    @staticmethod
    def validate_meal_behavior(behavior: Dict[str, Any]) -> List[str]:
        """
        Validate meal behavior data
        """
        errors = []
        
        if behavior.get('adherence_level') not in [adhere.value for adhere in MealAdherence]:
            errors.append("Invalid meal adherence level")
        
        return errors


class DataAnonymization:
    """
    Class to handle data anonymization for privacy protection
    """
    
    @staticmethod
    def anonymize_user_data(user_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Anonymize user data by removing or obfuscating personally identifiable information
        """
        anonymized_data = []
        
        for record in user_data:
            anon_record = record.copy()
            
            # Remove direct identifiers
            if 'user_id' in anon_record:
                anon_record['user_id'] = DataAnonymization._hash_identifier(anon_record['user_id'])
            
            # Generalize age to ranges if needed
            if 'age' in anon_record:
                anon_record['age_range'] = DataAnonymization._age_to_range(anon_record['age'])
                del anon_record['age']
            
            # Add anonymization timestamp
            anon_record['anonymized_at'] = datetime.now().isoformat()
            
            anonymized_data.append(anon_record)
        
        return anonymized_data
    
    @staticmethod
    def _hash_identifier(identifier: str) -> str:
        """
        Create a hash of the identifier for anonymization
        """
        import hashlib
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    @staticmethod
    def _age_to_range(age: int) -> str:
        """
        Convert specific age to age range
        """
        if age < 18:
            return "under_18"
        elif age < 25:
            return "18-24"
        elif age < 35:
            return "25-34"
        elif age < 45:
            return "35-44"
        elif age < 55:
            return "45-54"
        elif age < 65:
            return "55-64"
        else:
            return "65_plus"


# Example usage and testing
if __name__ == "__main__":
    # Initialize data collection
    collector = UserDataCollection()
    
    # Example user profile data (user-reported, not diagnostic)
    user_profile = {
        "age": 30,
        "weight": 75,  # User-reported
        "height": 175,  # User-reported
        "gender": "male",
        "fitness_goal": "strength",
        "experience_level": "intermediate",
        "equipment_available": ["dumbbells", "yoga_mat"],
        "dietary_preference": "vegetarian",
        "allergies_or_constraints": ["nuts"],
        "disclaimer_acknowledged": True,
        "consent_given": True
    }
    
    # Collect user profile
    user_id = collector.collect_user_profile(user_profile)
    print(f"Collected user profile with ID: {user_id}")
    
    # Example workout behavior data (user experience, not correctness)
    workout_behavior = {
        "workout_id": "workout_001",
        "completion_status": "completed",
        "perceived_difficulty": "moderate",
        "fatigue_level": "medium",
        "recovery_duration": "average",
        "notes": "Felt good, energy levels were appropriate",
        "user_experience_feedback": "Enjoyed the workout, right difficulty level"
    }
    
    # Collect workout behavior
    workout_record_id = collector.collect_workout_behavior(user_id, workout_behavior)
    print(f"Collected workout behavior with ID: {workout_record_id}")
    
    # Example meal behavior data (user experience, not nutritional correctness)
    meal_behavior = {
        "meal_id": "meal_001",
        "adherence_level": "followed",
        "enjoyment_rating": "high",
        "satisfaction_level": "satisfied",
        "hunger_level_after": "not_hungry",
        "notes": "Really enjoyed the flavors, felt satisfied",
        "user_experience_feedback": "Will make this recipe again"
    }
    
    # Collect meal behavior
    meal_record_id = collector.collect_meal_behavior(user_id, meal_behavior)
    print(f"Collected meal behavior with ID: {meal_record_id}")
    
    # Validate the collected data
    validator = DataValidation()
    
    # Load and validate the user profile
    profiles = collector._load_json_file(collector.user_profiles_file)
    if profiles:
        profile_errors = validator.validate_user_profile(profiles[-1])
        if profile_errors:
            print(f"Profile validation errors: {profile_errors}")
        else:
            print("Profile validation passed")
    
    # Anonymize example
    anonymizer = DataAnonymization()
    sample_data = [{"user_id": "test123", "age": 30, "weight": 75}]
    anonymized = anonymizer.anonymize_user_data(sample_data)
    print(f"Original: {sample_data}")
    print(f"Anonymized: {anonymized}")
    
    print("\nData collection pipeline initialized successfully!")
    print("All data represents user experience, not diagnostic measurements.")
    print("Ethical safeguards and privacy protections implemented.")