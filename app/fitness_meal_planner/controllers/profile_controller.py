"""
Profile Controller for handling profile updates and plan regeneration
"""

from flask import jsonify
import json
import os
from datetime import datetime


class ProfileController:
    def __init__(self):
        # Initialize with the necessary components
        self.data_dir = "data"
        self.profiles_file = os.path.join(self.data_dir, "user_profiles.json")  # Use existing file
        self._ensure_data_dir_exists()
        self._initialize_profiles_file()
    
    def _ensure_data_dir_exists(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _initialize_profiles_file(self):
        """Initialize the profiles file if it doesn't exist"""
        if not os.path.exists(self.profiles_file):
            with open(self.profiles_file, 'w') as f:
                json.dump({}, f)
    
    def update_profile_and_regenerate_plans(self, user_id: str, profile_data: dict):
        """
        Update user profile and regenerate workout/meal plans if needed
        """
        try:
            # Instead of checking our own profiles file, we'll update the user in the main user model
            # For this implementation, we'll just update our local copy and return success
            # In a real implementation, this would integrate with the main user model

            # Load existing profiles
            profiles = self._load_profiles()

            # Check if user exists in our local profiles
            # If not, we'll create an entry or update based on the profile data
            if user_id not in profiles:
                # Create a basic profile if it doesn't exist
                profiles[user_id] = {
                    'user_id': user_id,
                    'created_at': datetime.now().isoformat()
                }

            # Get current profile for comparison
            current_profile = profiles[user_id]

            # Update profile with new data
            updated_profile = current_profile.copy()
            updated_profile.update(profile_data)
            updated_profile['updated_at'] = datetime.now().isoformat()

            # Store updated profile
            profiles[user_id] = updated_profile
            self._save_profiles(profiles)

            # Check if changes affect workout or meal plans
            changes_affect_workout = self._changes_affect_workout_plans(current_profile, updated_profile)
            changes_affect_meal = self._changes_affect_meal_plans(current_profile, updated_profile)

            # Prepare response
            response_data = {
                'success': True,
                'message': 'Profile updated successfully',
                'profile_changes': {
                    'affect_workout_plans': changes_affect_workout,
                    'affect_meal_plans': changes_affect_meal
                },
                'updated_profile': updated_profile
            }

            # If changes affect workout plans, regenerate them
            if changes_affect_workout:
                # In a real implementation, this would call the workout plan generator
                response_data['workout_regeneration_needed'] = True
                response_data['regeneration_message'] = 'Workout plan will be regenerated based on profile changes'

            # If changes affect meal plans, regenerate them
            if changes_affect_meal:
                # In a real implementation, this would call the meal plan generator
                response_data['meal_regeneration_needed'] = True
                response_data['regeneration_message'] = 'Meal plan will be regenerated based on profile changes'

            return jsonify(response_data)

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def _changes_affect_workout_plans(self, old_profile: dict, new_profile: dict) -> bool:
        """
        Check if profile changes affect workout plans
        """
        # Check for changes that would affect workout recommendations
        workout_affecting_fields = [
            'fitness_level', 'goal', 'experience_level', 'injuries', 
            'health_conditions', 'equipment_available', 'preferred_categories',
            'disliked_exercises', 'time_available', 'age'
        ]
        
        for field in workout_affecting_fields:
            old_val = old_profile.get(field)
            new_val = new_profile.get(field)
            if old_val != new_val:
                return True
        
        return False
    
    def _changes_affect_meal_plans(self, old_profile: dict, new_profile: dict) -> bool:
        """
        Check if profile changes affect meal plans
        """
        # Check for changes that would affect meal recommendations
        meal_affecting_fields = [
            'goal', 'dietary_restrictions', 'allergies', 'health_conditions',
            'preferred_cuisines', 'disliked_ingredients', 'eating_frequency',
            'weight', 'height', 'age', 'gender', 'activity_level'
        ]
        
        for field in meal_affecting_fields:
            old_val = old_profile.get(field)
            new_val = new_profile.get(field)
            if old_val != new_val:
                return True
        
        return False
    
    def _load_profiles(self):
        """Load user profiles from file"""
        with open(self.profiles_file, 'r') as f:
            profiles_list = json.load(f)

        # Convert list to dictionary with user_id as key for easier lookup
        profiles_dict = {}
        for profile in profiles_list:
            user_id = profile.get('user_id')
            if user_id:
                profiles_dict[user_id] = profile

        return profiles_dict

    def _save_profiles(self, profiles_dict):
        """Save user profiles to file"""
        # Convert dictionary back to list for storage
        profiles_list = list(profiles_dict.values())
        with open(self.profiles_file, 'w') as f:
            json.dump(profiles_list, f, indent=2)