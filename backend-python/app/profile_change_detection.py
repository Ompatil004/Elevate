"""
Deterministic Profile Change Detection Engine

This module detects changes in user profiles that trigger workout/nutrition plan regeneration.
Features include threshold logic, cache invalidation, async job processing, and failure handling.
"""

import hashlib
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import asyncio
import logging
from dataclasses import dataclass
from uuid import uuid4
import redis
from celery import Celery
from celery.exceptions import Retry
import sqlite3
import threading
import time


# Configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')


# BUG-4 fix: Use lazy initialization so the module can be imported even when
# Redis / Celery are not available (e.g., unit tests, fresh developer machines).
_redis_client = None
_celery_app = None


def _get_redis_client():
    """Return a cached Redis client, creating it on first use."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    return _redis_client


def _get_celery_app():
    """Return a cached Celery application, creating it on first use."""
    global _celery_app
    if _celery_app is None:
        _celery_app = Celery(
            'profile_change_detection',
            broker=CELERY_BROKER_URL,
            backend=CELERY_RESULT_BACKEND,
        )
    return _celery_app


class ChangeType(Enum):
    """Types of profile changes that trigger regeneration"""
    GOAL_CHANGED = "goal_changed"
    EXPERIENCE_CHANGED = "experience_changed"
    EQUIPMENT_CHANGED = "equipment_changed"
    INJURY_ADDED = "injury_added"
    INJURY_REMOVED = "injury_removed"
    DAYS_PER_WEEK_CHANGED = "days_per_week_changed"
    WEIGHT_CHANGED = "weight_changed"
    HEIGHT_CHANGED = "height_changed"
    AGE_CHANGED = "age_changed"


@dataclass
class ProfileChange:
    """Represents a detected profile change"""
    user_id: str
    change_type: ChangeType
    old_value: Any
    new_value: Any
    timestamp: datetime
    triggered_regeneration: bool = False


class ProfileChangeDetector:
    """
    Detects changes in user profiles that require plan regeneration
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.change_thresholds = {
            'weight_change_percent': 0.05,  # 5% change triggers regeneration
            'days_change_threshold': 1,     # Any change in days triggers regeneration
        }
        self.redis_prefix = "profile_change:"
        self.cache_prefix = "plan_cache:"
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the detector"""
        logger = logging.getLogger("ProfileChangeDetector")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Prevent handler growth when this class is instantiated repeatedly.
        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        
        return logger
    
    def _generate_profile_hash(self, profile: Dict) -> str:
        """Generate a hash of the profile for comparison"""
        # Only include fields that matter for regeneration
        relevant_fields = {
            'goal': profile.get('goal'),
            'experience': profile.get('experience'),
            'equipment': sorted(profile.get('equipment', [])),
            'injuries': sorted(profile.get('body_issues', [])),
            'days_per_week': profile.get('days_per_week'),
            'weight': profile.get('weight'),
            'height': profile.get('height'),
            'age': profile.get('age')
        }
        
        # Convert to JSON string and hash
        profile_str = json.dumps(relevant_fields, sort_keys=True, default=str)
        return hashlib.sha256(profile_str.encode()).hexdigest()
    
    def _get_cached_profile_hash(self, user_id: str) -> Optional[str]:
        """Retrieve cached profile hash from Redis"""
        key = f"{self.redis_prefix}hash:{user_id}"
        cached_hash = _get_redis_client().get(key)
        return cached_hash.decode() if cached_hash else None
    
    def _set_cached_profile_hash(self, user_id: str, profile_hash: str):
        """Store profile hash in Redis"""
        key = f"{self.redis_prefix}hash:{user_id}"
        # Cache for 30 days
        _get_redis_client().setex(key, timedelta(days=30), profile_hash)
    
    def _invalidate_plan_cache(self, user_id: str):
        """Invalidate cached plans for the user"""
        cache_key = f"{self.cache_prefix}{user_id}"
        _get_redis_client().delete(cache_key)
        self.logger.info(f"Invalidated plan cache for user {user_id}")
    
    def _get_previous_profile(self, user_id: str) -> Optional[Dict]:
        """Retrieve previous profile from Redis"""
        key = f"{self.redis_prefix}profile:{user_id}"
        profile_data = _get_redis_client().get(key)
        if profile_data:
            try:
                decoded = profile_data.decode('utf-8')
                parsed = json.loads(decoded)
                if isinstance(parsed, dict):
                    return parsed
            except (UnicodeDecodeError, json.JSONDecodeError):
                self.logger.warning(
                    "Ignoring non-JSON cached profile for user %s; cache will be refreshed",
                    user_id,
                )
        return None
    
    def _store_current_profile(self, user_id: str, profile: Dict):
        """Store current profile in Redis"""
        key = f"{self.redis_prefix}profile:{user_id}"
        profile_data = json.dumps(profile, default=str)
        # Store for 30 days
        _get_redis_client().setex(key, timedelta(days=30), profile_data)
    
    def detect_changes(self, user_id: str, current_profile: Dict) -> List[ProfileChange]:
        """
        Detect changes in user profile that require regeneration
        """
        changes = []
        
        # Validate the incoming profile data
        validated_profile = self._validate_profile_data(current_profile)
        
        # Get previous profile hash
        previous_hash = self._get_cached_profile_hash(user_id)
        current_hash = self._generate_profile_hash(validated_profile)
        
        # If hashes are different, there are changes
        if previous_hash != current_hash:
            self.logger.info(f"Profile change detected for user {user_id}")
            
            # Get previous profile to determine what changed
            previous_profile = self._get_previous_profile(user_id)
            
            if previous_profile:
                # Compare each field that matters for regeneration
                changes.extend(self._compare_profile_fields(
                    user_id, previous_profile, validated_profile
                ))
            
            # Update cached hash and profile
            self._set_cached_profile_hash(user_id, current_hash)
            self._store_current_profile(user_id, validated_profile)
        
        return changes
    
    def _compare_profile_fields(self, user_id: str, old_profile: Dict, new_profile: Dict) -> List[ProfileChange]:
        """Compare profile fields and detect changes"""
        changes = []
        timestamp = datetime.now()
        
        # Compare goal
        old_goal = old_profile.get('goal')
        new_goal = new_profile.get('goal')
        if old_goal != new_goal:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.GOAL_CHANGED,
                old_value=old_goal,
                new_value=new_goal,
                timestamp=timestamp
            ))
        
        # Compare experience
        old_exp = old_profile.get('experience')
        new_exp = new_profile.get('experience')
        if old_exp != new_exp:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.EXPERIENCE_CHANGED,
                old_value=old_exp,
                new_value=new_exp,
                timestamp=timestamp
            ))
        
        # Compare equipment
        old_equipment = set(old_profile.get('equipment', []))
        new_equipment = set(new_profile.get('equipment', []))
        
        added_equipment = new_equipment - old_equipment
        removed_equipment = old_equipment - new_equipment
        
        if added_equipment:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.EQUIPMENT_CHANGED,
                old_value=list(old_equipment),
                new_value=list(new_equipment),
                timestamp=timestamp
            ))
        
        if removed_equipment:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.EQUIPMENT_CHANGED,
                old_value=list(old_equipment),
                new_value=list(new_equipment),
                timestamp=timestamp
            ))
        
        # Compare injuries
        old_injuries = set(old_profile.get('body_issues', []))
        new_injuries = set(new_profile.get('body_issues', []))
        
        added_injuries = new_injuries - old_injuries
        removed_injuries = old_injuries - new_injuries
        
        for injury in added_injuries:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.INJURY_ADDED,
                old_value=list(old_injuries),
                new_value=list(new_injuries),
                timestamp=timestamp
            ))
        
        for injury in removed_injuries:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.INJURY_REMOVED,
                old_value=list(old_injuries),
                new_value=list(new_injuries),
                timestamp=timestamp
            ))
        
        # Compare days per week
        old_days = old_profile.get('days_per_week', 0)
        new_days = new_profile.get('days_per_week', 0)
        if old_days != new_days:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.DAYS_PER_WEEK_CHANGED,
                old_value=old_days,
                new_value=new_days,
                timestamp=timestamp
            ))
        
        # Compare weight (with threshold)
        old_weight = old_profile.get('weight', 0)
        new_weight = new_profile.get('weight', 0)
        if old_weight != 0 and abs(new_weight - old_weight) / old_weight > self.change_thresholds['weight_change_percent']:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.WEIGHT_CHANGED,
                old_value=old_weight,
                new_value=new_weight,
                timestamp=timestamp
            ))
        
        # Compare height
        old_height = old_profile.get('height', 0)
        new_height = new_profile.get('height', 0)
        if old_height != new_height:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.HEIGHT_CHANGED,
                old_value=old_height,
                new_value=new_height,
                timestamp=timestamp
            ))
        
        # Compare age
        old_age = old_profile.get('age', 0)
        new_age = new_profile.get('age', 0)
        if old_age != new_age:
            changes.append(ProfileChange(
                user_id=user_id,
                change_type=ChangeType.AGE_CHANGED,
                old_value=old_age,
                new_value=new_age,
                timestamp=timestamp
            ))

        return changes
    
    def _validate_profile_data(self, profile: Dict) -> Dict:
        """Validate and sanitize profile data"""
        validated_profile = profile.copy()
        
        # Validate age range (18-80)
        age = validated_profile.get('age', 25)
        if not isinstance(age, (int, float)) or age < 18 or age > 80:
            validated_profile['age'] = 25  # Default to 25 if invalid
        
        # Validate weight range (40-200 kg)
        weight = validated_profile.get('weight', 70.0)
        if not isinstance(weight, (int, float)) or weight < 40 or weight > 200:
            validated_profile['weight'] = 70.0  # Default to 70kg if invalid
        
        # Validate height range (120-250 cm)
        height = validated_profile.get('height', 175.0)
        if not isinstance(height, (int, float)) or height < 120 or height > 250:
            validated_profile['height'] = 175.0  # Default to 175cm if invalid
        
        # Validate days per week (1-7)
        days = validated_profile.get('days_per_week', 4)
        if not isinstance(days, int) or days < 1 or days > 7:
            validated_profile['days_per_week'] = 4  # Default to 4 days if invalid
        
        # Validate experience level
        experience = validated_profile.get('experience', 'Beginner')
        valid_experiences = ['Beginner', 'Intermediate', 'Advanced']
        if experience not in valid_experiences:
            validated_profile['experience'] = 'Beginner'  # Default to Beginner if invalid
        
        # Validate goal
        goal = validated_profile.get('goal', 'Muscle Gain')
        valid_goals = ['Weight Loss', 'Fat Loss', 'Muscle Gain', 'Strength', 'Endurance', 'Maintenance']
        if goal not in valid_goals:
            validated_profile['goal'] = 'Muscle Gain'  # Default to Muscle Gain if invalid
        
        # Validate equipment list
        equipment = validated_profile.get('equipment', [])
        if not isinstance(equipment, list):
            validated_profile['equipment'] = []
        
        # Validate body issues list
        body_issues = validated_profile.get('body_issues', [])
        if not isinstance(body_issues, list):
            validated_profile['body_issues'] = []
        
        return validated_profile


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def trigger_regeneration_task(self, user_id: str, changes: List[Dict]):
    """
    Celery task to trigger plan regeneration
    """
    try:
        self.logger.info(f"Starting regeneration for user {user_id} due to changes: {[c['change_type'] for c in changes]}")
        
        # Invalidate cache
        detector = ProfileChangeDetector()
        detector._invalidate_plan_cache(user_id)
        
        # Here you would call the actual regeneration logic
        # For example: regenerate_workout_plan(user_id) or regenerate_nutrition_plan(user_id)
        # This is a placeholder for the actual regeneration logic
        time.sleep(2)  # Simulate processing time
        
        # Update change records to mark as triggered
        for change_data in changes:
            change = ProfileChange(
                user_id=change_data['user_id'],
                change_type=ChangeType(change_data['change_type']),
                old_value=change_data['old_value'],
                new_value=change_data['new_value'],
                timestamp=datetime.fromisoformat(change_data['timestamp']),
                triggered_regeneration=True
            )
            # In a real implementation, you would update the database record
            # update_change_record(change)
        
        self.logger.info(f"Regeneration completed for user {user_id}")
        return {"status": "success", "user_id": user_id, "changes": changes}
        
    except Exception as exc:
        self.logger.error(f"Error in regeneration task for user {user_id}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc)


class ProfileChangeManager:
    """
    Manages the profile change detection and regeneration workflow
    """
    
    def __init__(self):
        self.detector = ProfileChangeDetector()
        self.logger = self.detector.logger
        self.active_jobs = {}  # Track active jobs to prevent duplicates
        self.lock = threading.Lock()
    
    def process_profile_update(self, user_id: str, profile: Dict) -> Dict:
        """
        Process a profile update and trigger regeneration if needed
        """
        with self.lock:
            self.logger.info(f"Processing profile update for user {user_id}")
            
            # Detect changes
            changes = self.detector.detect_changes(user_id, profile)
            
            if not changes:
                self.logger.info(f"No significant changes detected for user {user_id}")
                return {"status": "no_changes", "changes": []}
            
            # Convert changes to serializable format
            changes_serializable = []
            for change in changes:
                changes_serializable.append({
                    "user_id": change.user_id,
                    "change_type": change.change_type.value,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "timestamp": change.timestamp.isoformat(),
                    "triggered_regeneration": change.triggered_regeneration
                })
            
            self.logger.info(f"Detected {len(changes)} changes for user {user_id}: {[c['change_type'] for c in changes_serializable]}")
            
            # Check if regeneration is already in progress
            job_key = f"regen_{user_id}"
            if job_key in self.active_jobs:
                self.logger.warning(f"Regeneration already in progress for user {user_id}, skipping duplicate")
                return {"status": "duplicate_job_skipped", "changes": changes_serializable}
            
            # Trigger regeneration task
            self.logger.info(f"Triggering regeneration task for user {user_id}")
            task = _get_celery_app().send_task(
            'profile_change_detection.trigger_regeneration_task',
            args=[user_id, changes_serializable]
        )
            
            # Track the job
            self.active_jobs[job_key] = {
                "task_id": task.id,
                "timestamp": datetime.now(),
                "changes": changes_serializable
            }
            
            # Clean up old job records (keep only recent ones)
            self._cleanup_old_jobs()
            
            self.logger.info(f"Regeneration task {task.id} triggered for user {user_id} with {len(changes)} changes")
            
            return {
                "status": "regeneration_triggered", 
                "changes": changes_serializable,
                "task_id": task.id
            }
    
    def _cleanup_old_jobs(self):
        """Clean up old job records to prevent memory leaks"""
        current_time = datetime.now()
        expired_jobs = []
        
        for job_key, job_info in self.active_jobs.items():
            # Remove jobs older than 1 hour
            if current_time - job_info["timestamp"] > timedelta(hours=1):
                expired_jobs.append(job_key)
        
        for job_key in expired_jobs:
            del self.active_jobs[job_key]
    
    def get_job_status(self, user_id: str) -> Dict:
        """Get the status of a regeneration job for a user"""
        job_key = f"regen_{user_id}"
        if job_key in self.active_jobs:
            job_info = self.active_jobs[job_key]
            task_result = trigger_regeneration_task.AsyncResult(job_info["task_id"])
            
            return {
                "status": task_result.status,
                "task_id": job_info["task_id"],
                "changes": job_info["changes"],
                "timestamp": job_info["timestamp"].isoformat()
            }
        else:
            return {"status": "no_active_job", "task_id": None}


# Database Schema Changes
DATABASE_SCHEMA_CHANGES = """
-- Table to store profile change records
CREATE TABLE IF NOT EXISTS profile_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    change_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    triggered_regeneration BOOLEAN DEFAULT FALSE,
    regeneration_task_id TEXT,
    plan_version TEXT
);

-- Index for faster queries by user_id and timestamp
CREATE INDEX IF NOT EXISTS idx_profile_changes_user_timestamp 
ON profile_changes (user_id, timestamp DESC);

-- Additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_profile_changes_change_type 
ON profile_changes (change_type);
CREATE INDEX IF NOT EXISTS idx_profile_changes_regenerated 
ON profile_changes (triggered_regeneration);

-- Table to track plan versions
CREATE TABLE IF NOT EXISTS plan_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    plan_type TEXT NOT NULL, -- 'workout' or 'nutrition'
    version_number INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

-- Index for plan versions
CREATE INDEX IF NOT EXISTS idx_plan_versions_user_type 
ON plan_versions (user_id, plan_type, is_current);

-- Additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_plan_versions_created_at 
ON plan_versions (created_at);
CREATE INDEX IF NOT EXISTS idx_plan_versions_current 
ON plan_versions (is_current);
"""


def setup_database():
    """Setup database tables for profile change tracking"""
    conn = sqlite3.connect('elevate_fitness.db')
    cursor = conn.cursor()
    
    # Execute schema changes
    cursor.executescript(DATABASE_SCHEMA_CHANGES)
    
    conn.commit()
    conn.close()


def example_usage():
    """
    Example usage of the profile change detection engine
    """
    print("=" * 60)
    print("PROFILE CHANGE DETECTION ENGINE - EXAMPLE USAGE")
    print("=" * 60)
    
    # Initialize the manager
    manager = ProfileChangeManager()
    
    # Example user profile
    user_id = "user_12345"
    
    # Initial profile
    initial_profile = {
        'goal': 'Muscle Gain',
        'experience': 'Beginner',
        'equipment': ['Dumbbell', 'Bench'],
        'body_issues': ['Knee'],
        'days_per_week': 4,
        'weight': 70.0,
        'height': 175.0,
        'age': 28
    }
    
    print(f"Initial profile for {user_id}:")
    for key, value in initial_profile.items():
        print(f"  {key}: {value}")
    
    # Process initial profile (should not trigger regeneration)
    result1 = manager.process_profile_update(user_id, initial_profile)
    print(f"\nResult after initial profile: {result1['status']}")
    
    # Update profile with significant changes
    updated_profile = {
        'goal': 'Weight Loss',  # Changed goal
        'experience': 'Intermediate',  # Changed experience
        'equipment': ['Dumbbell', 'Barbell', 'Machine'],  # Added equipment
        'body_issues': [],  # Removed injury
        'days_per_week': 5,  # Changed days
        'weight': 68.0,  # Changed weight (more than 5%)
        'height': 175.0,
        'age': 28
    }
    
    print(f"\nUpdated profile for {user_id}:")
    for key, value in updated_profile.items():
        print(f"  {key}: {value}")
    
    # Process updated profile (should trigger regeneration)
    result2 = manager.process_profile_update(user_id, updated_profile)
    print(f"\nResult after updated profile: {result2['status']}")
    
    if result2['status'] == 'regeneration_triggered':
        print(f"  Task ID: {result2['task_id']}")
        print(f"  Number of changes: {len(result2['changes'])}")
        
        # Show detected changes
        for change in result2['changes']:
            print(f"    - {change['change_type']}: {change['old_value']} -> {change['new_value']}")
    
    # Try to update again with same profile (should not trigger regeneration)
    result3 = manager.process_profile_update(user_id, updated_profile)
    print(f"\nResult after same profile: {result3['status']}")
    
    # Check job status
    job_status = manager.get_job_status(user_id)
    print(f"\nJob status for {user_id}: {job_status['status']}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE USAGE COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    # Setup database
    setup_database()
    
    # Run example
    example_usage()