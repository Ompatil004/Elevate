"""
User Model for managing user profiles and preferences
"""

import json
import os
from datetime import datetime


class UserModel:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.preferences_file = os.path.join(data_dir, "user_preferences.json")
        self._ensure_data_dir_exists()
        self._initialize_users_file()
        self._initialize_preferences_file()

    def _ensure_data_dir_exists(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _initialize_users_file(self):
        """Initialize the users file if it doesn't exist"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)

    def _initialize_preferences_file(self):
        """Initialize the preferences file if it doesn't exist"""
        if not os.path.exists(self.preferences_file):
            with open(self.preferences_file, 'w') as f:
                json.dump({}, f)

    def create_user(self, user_data):
        """Create a new user profile"""
        # Load existing users
        users = self._load_users()

        # Generate new user ID
        user_id = len(users) + 1

        # Set default values if not provided
        user_defaults = {
            'fitness_level': 'beginner',
            'goal': 'general_fitness',
            'age': 30,
            'gender': 'male',
            'weight': 70,  # kg
            'height': 170,  # cm
            'activity_level': 'moderate',
            'injuries': [],
            'health_conditions': [],
            'equipment_available': ['none'],
            'preferred_categories': [],
            'disliked_exercises': [],
            'preferred_cuisines': [],
            'disliked_ingredients': [],
            'dietary_restrictions': [],
            'allergies': [],
            'exercise_history': [],
            'meal_history': [],
            'performance_data': {},
            'dietary_preferences': {}
        }

        # Merge defaults with provided data
        for key, value in user_defaults.items():
            if key not in user_data:
                user_data[key] = value

        # Add timestamp
        user_data['created_at'] = datetime.now().isoformat()
        user_data['updated_at'] = datetime.now().isoformat()

        # Add user to dictionary
        users[user_id] = user_data

        # Save updated users
        self._save_users(users)

        # Initialize empty preferences for this user
        preferences = self._load_preferences()
        preferences[str(user_id)] = {
            'exercise_preferences': {},
            'meal_preferences': {},
            'feedback': [],
            'last_updated': datetime.now().isoformat()
        }
        self._save_preferences(preferences)

        return user_id

    def get_user(self, user_id):
        """Get user profile by ID"""
        users = self._load_users()
        user = users.get(str(user_id))

        if user:
            # Add preferences to user data
            preferences = self._load_preferences()
            user_prefs = preferences.get(str(user_id), {})
            user['preferences'] = user_prefs

        return user

    def update_user(self, user_id, user_data):
        """Update user profile"""
        users = self._load_users()
        user_id_str = str(user_id)

        if user_id_str in users:
            # Update with new data while preserving creation time
            existing_user = users[user_id_str]
            existing_user.update(user_data)
            existing_user['updated_at'] = datetime.now().isoformat()

            # Save updated users
            self._save_users(users)
            return True
        else:
            return False

    def update_user_preferences(self, user_id, preference_data):
        """Update user preferences"""
        preferences = self._load_preferences()
        user_id_str = str(user_id)

        if user_id_str not in preferences:
            preferences[user_id_str] = {
                'exercise_preferences': {},
                'meal_preferences': {},
                'feedback': [],
                'last_updated': datetime.now().isoformat()
            }

        # Update preferences
        user_prefs = preferences[user_id_str]
        if 'exercise_preferences' in preference_data:
            user_prefs['exercise_preferences'].update(preference_data['exercise_preferences'])
        if 'meal_preferences' in preference_data:
            user_prefs['meal_preferences'].update(preference_data['meal_preferences'])
        if 'feedback' in preference_data:
            user_prefs['feedback'].extend(preference_data['feedback'])

        user_prefs['last_updated'] = datetime.now().isoformat()

        # Save updated preferences
        self._save_preferences(preferences)
        return True

    def add_exercise_feedback(self, user_id, exercise_name, rating, performance_data=None):
        """Add feedback for an exercise"""
        user = self.get_user(user_id)
        if not user:
            return False

        # Update exercise history
        exercise_entry = {
            'exercise': exercise_name,
            'date': datetime.now().isoformat(),
            'rating': rating
        }

        if performance_data:
            exercise_entry.update(performance_data)

        user['exercise_history'].append(exercise_entry)

        # Update performance data for this exercise
        if exercise_name not in user['performance_data']:
            user['performance_data'][exercise_name] = {
                'attempts': 0,
                'avg_rating': 0,
                'improvement_trend': 0,
                'difficulty_rating': 5
            }

        perf_data = user['performance_data'][exercise_name]
        perf_data['attempts'] += 1
        perf_data['avg_rating'] = ((perf_data['avg_rating'] * (perf_data['attempts'] - 1)) + rating) / perf_data['attempts']
        perf_data['difficulty_rating'] = rating  # Simplified: use rating as difficulty indicator

        # Update user
        return self.update_user(user_id, {
            'exercise_history': user['exercise_history'],
            'performance_data': user['performance_data']
        })

    def add_meal_feedback(self, user_id, meal_name, rating, nutrition_feedback=None):
        """Add feedback for a meal"""
        user = self.get_user(user_id)
        if not user:
            return False

        # Update meal history
        meal_entry = {
            'meal': meal_name,
            'date': datetime.now().isoformat(),
            'rating': rating
        }

        if nutrition_feedback:
            meal_entry.update(nutrition_feedback)

        user['meal_history'].append(meal_entry)

        # Update user
        return self.update_user(user_id, {
            'meal_history': user['meal_history']
        })

    def get_user_preferences(self, user_id):
        """Get user preferences"""
        preferences = self._load_preferences()
        return preferences.get(str(user_id), {})

    def _load_users(self):
        """Load users from file"""
        with open(self.users_file, 'r') as f:
            return json.load(f)

    def _save_users(self, users):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)

    def _load_preferences(self):
        """Load preferences from file"""
        with open(self.preferences_file, 'r') as f:
            return json.load(f)

    def _save_preferences(self, preferences):
        """Save preferences to file"""
        with open(self.preferences_file, 'w') as f:
            json.dump(preferences, f, indent=2)