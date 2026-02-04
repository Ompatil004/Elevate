"""
Workout Model for managing workout plans and history
"""

import json
import os
from datetime import datetime


class WorkoutModel:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.workouts_file = os.path.join(data_dir, "workouts.json")
        self._ensure_data_dir_exists()
        self._initialize_workouts_file()

    def _ensure_data_dir_exists(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _initialize_workouts_file(self):
        """Initialize the workouts file if it doesn't exist"""
        if not os.path.exists(self.workouts_file):
            with open(self.workouts_file, 'w') as f:
                json.dump({}, f)

    def save_workout_plan(self, user_id, workout_plan):
        """Save a workout plan for a user"""
        workouts = self._load_workouts()
        
        # Generate new workout ID
        workout_id = len([wk for wks in workouts.values() for wk in wks]) + 1
        
        # Add timestamp and user reference
        workout_plan['workout_id'] = workout_id
        workout_plan['user_id'] = user_id
        workout_plan['created_at'] = datetime.now().isoformat()
        workout_plan['updated_at'] = datetime.now().isoformat()
        
        # Add to user's workout history
        user_id_str = str(user_id)
        if user_id_str not in workouts:
            workouts[user_id_str] = []
        
        workouts[user_id_str].append(workout_plan)
        
        # Save updated workouts
        self._save_workouts(workouts)
        
        return workout_id

    def get_workout_history(self, user_id):
        """Get workout history for a user"""
        workouts = self._load_workouts()
        user_id_str = str(user_id)
        return workouts.get(user_id_str, [])

    def _load_workouts(self):
        """Load workouts from file"""
        with open(self.workouts_file, 'r') as f:
            return json.load(f)

    def _save_workouts(self, workouts):
        """Save workouts to file"""
        with open(self.workouts_file, 'w') as f:
            json.dump(workouts, f, indent=2)