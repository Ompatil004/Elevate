"""
Exercise Rules module for rule-based exercise selection and safety constraints
"""

class ExerciseRules:
    def __init__(self):
        # Define exercise categories and their properties
        self.exercise_categories = {
            'cardio': {
                'beginner_max_duration': 20,  # minutes
                'equipment_required': [],
                'intensity_levels': {'beginner': 5, 'intermediate': 7, 'advanced': 9}
            },
            'strength': {
                'beginner_max_sets': 2,
                'equipment_required': ['weights', 'resistance_bands'],
                'intensity_levels': {'beginner': 6, 'intermediate': 8, 'advanced': 9}
            },
            'flexibility': {
                'beginner_max_duration': 15,
                'equipment_required': ['yoga_mat'],
                'intensity_levels': {'beginner': 3, 'intermediate': 5, 'advanced': 7}
            },
            'hiit': {
                'beginner_restricted': True,  # Beginners shouldn't do HIIT
                'equipment_required': [],
                'intensity_levels': {'intermediate': 8, 'advanced': 10}
            },
            'core': {
                'beginner_max_duration': 10,
                'equipment_required': ['yoga_mat'],
                'intensity_levels': {'beginner': 4, 'intermediate': 6, 'advanced': 8}
            }
        }

        # Define injury exclusions
        self.injury_exclusions = {
            'knee_injury': [
                'squats', 'lunges', 'jumping_jacks', 'burpees',
                'running', 'high_knees', 'mountain_climbers', 'step-ups',
                'box_jumps', 'plyometric_lunges', 'jump_squats'
            ],
            'back_injury': [
                'deadlifts', 'situps', 'planks', 'superman',
                'back_extensions', 'good_mornings', 'romanian_deadlifts',
                'hyperextensions', 'weighted_crunches', 'reverse_crunches'
            ],
            'shoulder_injury': [
                'pushups', 'shoulder_press', 'pullups',
                'arm_circles', 'plank_to_pushup', 'pike_pushups',
                'handstand_pushups', 'overhead_press', 'lateral_raises'
            ],
            'wrist_injury': [
                'pushups', 'planks', 'dips', 'handstand',
                'plank_to_pushup', 'pike_pushups', 'yoga_poses_with_wrist_load'
            ],
            'elbow_injury': [
                'pushups', 'tricep_dips', 'bicep_curls',
                'hammer_curls', 'tricep_extensions', 'close_grip_pushups'
            ]
        }

        # Define equipment availability mapping
        self.equipment_mapping = {
            'dumbbells': ['bicep_curls', 'shoulder_press', 'goblet_squats', 'deadlifts', 'rows', 'flyes'],
            'resistance_bands': ['band_pull_aparts', 'band_assisted_pullups', 'band_rows', 'band_squats'],
            'yoga_mat': ['planks', 'pushups', 'stretching', 'yoga', 'pilates', 'abs_exercises'],
            'kettlebell': ['kettlebell_swings', 'goblet_squats', 'kettlebell_snatches', 'halos'],
            'pullup_bar': ['pullups', 'hanging_leg_raises', 'chinups', 'hanging_knee_raises'],
            'exercise_bike': ['stationary_cycling', 'interval_training'],
            'treadmill': ['walking', 'running', 'incline_walking'],
            'elliptical': ['elliptical_training', 'low_impact_cardio']
        }

        # Define exercise compatibility rules
        self.compatibility_rules = {
            # Exercises that shouldn't be done together in the same session
            'conflicting_muscles': [
                ('chest_press', 'rear_delt_flies'),  # Opposing muscles
                ('bicep_curls', 'tricep_extensions'),  # Opposing muscles
            ],
            # Exercises that should be done in sequence for optimal results
            'synergistic_pairs': [
                ('warmup', 'main_exercise'),
                ('compound_movement', 'isolation_movement'),
                ('strength_exercise', 'cardio_exercise'),
            ]
        }

        # Define safety rules
        self.safety_rules = {
            'minimum_rest_time': {
                'strength': 60,  # seconds between sets
                'hiit': 30,
                'cardio': 15
            },
            'maximum_volume_per_muscle_group_per_week': {
                'chest': 12,  # sets per week
                'back': 12,
                'legs': 16,
                'shoulders': 10,
                'arms': 8,
                'core': 10
            },
            'overload_principle': {
                'weekly_increase_percentage': 5  # percent increase in volume/load
            }
        }

    def filter_exercises_by_rules(self, user_profile):
        """Apply rule-based filtering to exercises based on user profile"""
        # Start with all exercises
        all_exercises = self._get_all_exercises()

        # Apply injury exclusions
        filtered_exercises = self._apply_injury_exclusions(all_exercises, user_profile)

        # Apply equipment availability
        filtered_exercises = self._apply_equipment_filter(filtered_exercises, user_profile)

        # Apply beginner protections
        filtered_exercises = self._apply_beginner_protections(filtered_exercises, user_profile)

        # Apply health condition exclusions
        filtered_exercises = self._apply_health_condition_exclusions(filtered_exercises, user_profile)

        # Apply age-based restrictions
        filtered_exercises = self._apply_age_restrictions(filtered_exercises, user_profile)

        # Apply experience-based volume limits
        filtered_exercises = self._apply_volume_limits(filtered_exercises, user_profile)

        # Apply exercise compatibility rules
        filtered_exercises = self._apply_compatibility_rules(filtered_exercises, user_profile)

        return filtered_exercises

    def determine_frequency(self, user_profile):
        """Determine workout frequency based on user profile"""
        fitness_level = user_profile.get('fitness_level', 'beginner')
        time_availability = user_profile.get('time_availability', 3)  # hours per week
        
        if fitness_level == 'beginner':
            return min(3, time_availability)  # Max 3 days for beginners
        elif fitness_level == 'intermediate':
            return min(4, time_availability)
        else:  # advanced
            return min(5, time_availability)

    def determine_duration(self, user_profile):
        """Determine workout duration based on user profile"""
        fitness_level = user_profile.get('fitness_level', 'beginner')
        
        if fitness_level == 'beginner':
            return 30  # minutes
        elif fitness_level == 'intermediate':
            return 45
        else:  # advanced
            return 60

    def get_applied_rules(self):
        """Return list of rules applied during filtering"""
        return [
            "Injury-based exercise exclusions applied",
            "Equipment availability filtering applied",
            "Beginner volume/intensity protections applied",
            "Health condition exclusions applied",
            "Rest day enforcement applied"
        ]

    def _get_all_exercises(self):
        """Get all available exercises"""
        return [
            {'name': 'pushups', 'category': 'strength', 'difficulty': 'beginner'},
            {'name': 'squats', 'category': 'strength', 'difficulty': 'beginner'},
            {'name': 'planks', 'category': 'core', 'difficulty': 'beginner'},
            {'name': 'lunges', 'category': 'strength', 'difficulty': 'intermediate'},
            {'name': 'burpees', 'category': 'hiit', 'difficulty': 'intermediate'},
            {'name': 'jumping_jacks', 'category': 'cardio', 'difficulty': 'beginner'},
            {'name': 'mountain_climbers', 'category': 'hiit', 'difficulty': 'intermediate'},
            {'name': 'deadlifts', 'category': 'strength', 'difficulty': 'advanced'},
            {'name': 'pullups', 'category': 'strength', 'difficulty': 'intermediate'},
            {'name': 'bicep_curls', 'category': 'strength', 'difficulty': 'beginner'},
            {'name': 'shoulder_press', 'category': 'strength', 'difficulty': 'intermediate'},
            {'name': 'tricep_dips', 'category': 'strength', 'difficulty': 'beginner'},
            {'name': 'leg_raises', 'category': 'core', 'difficulty': 'beginner'},
            {'name': 'Russian_twists', 'category': 'core', 'difficulty': 'intermediate'},
            {'name': 'high_knees', 'category': 'cardio', 'difficulty': 'beginner'},
            {'name': 'running', 'category': 'cardio', 'difficulty': 'intermediate'},
            {'name': 'walking', 'category': 'cardio', 'difficulty': 'beginner'},
            {'name': 'yoga_stretches', 'category': 'flexibility', 'difficulty': 'beginner'},
            {'name': 'hip_flexor_stretches', 'category': 'flexibility', 'difficulty': 'beginner'},
            {'name': 'shoulder_stretches', 'category': 'flexibility', 'difficulty': 'beginner'}
        ]

    def _apply_injury_exclusions(self, exercises, user_profile):
        """Filter out exercises based on user injuries"""
        injuries = user_profile.get('injuries', [])
        excluded_exercises = set()
        
        for injury in injuries:
            if injury in self.injury_exclusions:
                excluded_exercises.update(self.injury_exclusions[injury])
        
        return [ex for ex in exercises if ex['name'] not in excluded_exercises]

    def _apply_equipment_filter(self, exercises, user_profile):
        """Filter exercises based on available equipment"""
        available_equipment = user_profile.get('equipment_available', [])
        
        # If no equipment restrictions, return all exercises
        if 'any' in available_equipment or 'all' in available_equipment:
            return exercises
            
        # Find exercises that match available equipment
        filtered_exercises = []
        for exercise in exercises:
            # Check if exercise requires specific equipment
            category = exercise['category']
            if category in self.exercise_categories:
                required_equipment = self.exercise_categories[category]['equipment_required']
                
                # If no equipment required, include the exercise
                if not required_equipment:
                    filtered_exercises.append(exercise)
                # If some equipment is required, check if user has it
                elif any(eq in available_equipment for eq in required_equipment):
                    filtered_exercises.append(exercise)
            else:
                # If category not defined in our rules, include by default
                filtered_exercises.append(exercise)
        
        return filtered_exercises

    def _apply_beginner_protections(self, exercises, user_profile):
        """Apply protections for beginners"""
        fitness_level = user_profile.get('fitness_level', 'beginner')
        
        if fitness_level != 'beginner':
            return exercises
            
        # Remove HIIT exercises for beginners
        filtered_exercises = []
        for exercise in exercises:
            category = exercise['category']
            if category in self.exercise_categories:
                if self.exercise_categories[category].get('beginner_restricted', False):
                    continue
            filtered_exercises.append(exercise)
            
        return filtered_exercises

    def _apply_health_condition_exclusions(self, exercises, user_profile):
        """Filter out exercises based on health conditions"""
        health_conditions = user_profile.get('health_conditions', [])

        # For cardiac conditions, exclude high-intensity exercises
        if 'cardiac_issues' in health_conditions:
            exercises = [ex for ex in exercises if ex['category'] not in ['hiit'] or ex['difficulty'] != 'advanced']

        # For hypertension, avoid exercises that cause rapid BP spikes
        if 'hypertension' in health_conditions:
            exercises = [ex for ex in exercises if ex['name'] not in ['heavy_deadlifts', 'valsalva_maneuver_exercises']]

        # For diabetes, encourage regular moderate activity
        if 'diabetes' in health_conditions:
            exercises = [ex for ex in exercises if ex['category'] in ['cardio', 'strength', 'flexibility']]

        return exercises

    def _apply_age_restrictions(self, exercises, user_profile):
        """Apply age-based exercise restrictions"""
        age = user_profile.get('age', 30)

        # For seniors (65+), avoid high-impact exercises
        if age >= 65:
            exercises = [ex for ex in exercises if 'jumping' not in ex['name'] and ex['category'] != 'hiit']

        # For younger individuals, ensure proper form focus
        if age < 18:
            exercises = [ex for ex in exercises if ex['name'] not in ['heavy_weightlifting', 'maximal_exertion']]

        return exercises

    def _apply_volume_limits(self, exercises, user_profile):
        """Apply volume limits based on experience level"""
        fitness_level = user_profile.get('fitness_level', 'beginner')

        if fitness_level == 'beginner':
            # Limit total exercises per session
            max_exercises = 6
            return exercises[:max_exercises]
        elif fitness_level == 'intermediate':
            max_exercises = 8
            return exercises[:max_exercises]
        else:  # advanced
            max_exercises = 12
            return exercises[:max_exercises]

    def _apply_compatibility_rules(self, exercises, user_profile):
        """Apply exercise compatibility rules"""
        # Remove conflicting muscle group exercises if needed
        filtered_exercises = []
        used_muscle_groups = set()

        for exercise in exercises:
            primary_muscles = exercise.get('primary_muscles', [])

            # Skip if this exercise conflicts with already selected muscles
            # For simplicity, we'll just ensure we don't overtrain the same muscle group
            should_add = True
            for muscle in primary_muscles:
                if muscle in used_muscle_groups:
                    # Allow if it's a synergistic pair
                    is_synergistic = any(
                        (exercise['name'], existing_ex) in self.compatibility_rules['synergistic_pairs'] or
                        (existing_ex, exercise['name']) in self.compatibility_rules['synergistic_pairs']
                        for existing_ex in [ex['name'] for ex in filtered_exercises]
                    )
                    if not is_synergistic:
                        should_add = False
                        break

            if should_add:
                filtered_exercises.append(exercise)
                used_muscle_groups.update(primary_muscles)

        return filtered_exercises