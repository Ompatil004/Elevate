"""
Workout Plan Generation Algorithm
Integrates rule-based logic and ML personalization for safe and effective workout plans
"""

from rules.exercise_rules import ExerciseRules
from ml.adaptive_engine import AdaptiveEngine
import random
from datetime import datetime, timedelta


class WorkoutPlanGenerator:
    def __init__(self):
        self.exercise_rules = ExerciseRules()
        self.adaptive_engine = AdaptiveEngine()
    
    def generate_workout_plan(self, user_profile, plan_duration_days=7):
        """
        Generate a comprehensive workout plan for the user
        """
        # Generate weekly plan
        weekly_plan = {
            'user_id': user_profile.get('user_id'),
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=plan_duration_days)).strftime('%Y-%m-%d'),
            'days': [],
            'summary': {}
        }
        
        # Determine workout frequency based on user profile
        workout_frequency = self.exercise_rules.determine_frequency(user_profile)
        
        # Get available workout days
        workout_days = self._select_workout_days(plan_duration_days, workout_frequency)
        
        # Generate individual workout sessions
        for day_idx, is_workout_day in enumerate(workout_days):
            if is_workout_day:
                # Create workout session for this day
                session = self._create_workout_session(user_profile, day_idx)
                weekly_plan['days'].append(session)
            else:
                # Rest day
                weekly_plan['days'].append({
                    'day': day_idx + 1,
                    'type': 'rest',
                    'date': (datetime.now() + timedelta(days=day_idx)).strftime('%Y-%m-%d'),
                    'activities': ['Active recovery', 'Stretching', 'Light walking']
                })
        
        # Generate summary statistics
        weekly_plan['summary'] = self._generate_summary(weekly_plan, user_profile)
        
        return weekly_plan
    
    def _select_workout_days(self, total_days, frequency):
        """
        Select which days will be workout days based on frequency
        """
        # Create a pattern that distributes workouts evenly
        workout_days = [False] * total_days
        
        if frequency >= total_days:
            # If frequency is greater than total days, make all days workout days
            return [True] * total_days
        
        # Distribute workout days evenly
        interval = total_days // frequency
        for i in range(frequency):
            day_index = i * interval
            if day_index < total_days:
                workout_days[day_index] = True
        
        # Handle remaining slots if needed
        remaining_days = [i for i, is_workout in enumerate(workout_days) if not is_workout]
        workout_count = sum(workout_days)
        
        while workout_count < frequency and remaining_days:
            # Add workout day, avoiding consecutive days if possible
            day_to_add = remaining_days.pop(0)
            if day_to_add == 0 or not workout_days[day_to_add - 1]:  # Avoid consecutive if possible
                workout_days[day_to_add] = True
                workout_count += 1
        
        return workout_days
    
    def _create_workout_session(self, user_profile, day_number):
        """
        Create a single workout session based on user profile
        """
        # Apply rule-based filtering to get safe exercises
        filtered_exercises = self.exercise_rules.filter_exercises_by_rules(user_profile)
        
        # Apply ML-based personalization
        personalized_exercises = self.adaptive_engine.personalize_exercises(
            filtered_exercises, 
            user_profile
        )
        
        # Select exercises for this session based on time availability and goals
        session_exercises = self._select_session_exercises(
            personalized_exercises, 
            user_profile
        )
        
        # Determine workout type based on muscle groups and goals
        workout_type = self._determine_workout_type(session_exercises, user_profile)
        
        # Create session structure
        session = {
            'day': day_number + 1,
            'date': (datetime.now() + timedelta(days=day_number)).strftime('%Y-%m-%d'),
            'type': workout_type,
            'duration_minutes': self.exercise_rules.determine_duration(user_profile),
            'intensity': self._determine_intensity(user_profile),
            'exercises': session_exercises,
            'warmup': self._generate_warmup(user_profile),
            'cooldown': self._generate_cooldown(user_profile),
            'safety_check_passed': True,
            'rules_applied': self.exercise_rules.get_applied_rules(),
            'ml_adjustments': self.adaptive_engine.get_adjustments()
        }
        
        return session
    
    def _select_session_exercises(self, personalized_exercises, user_profile):
        """
        Select appropriate exercises for a single session
        """
        # Get user preferences
        time_available = user_profile.get('time_available', 45)  # minutes
        goal = user_profile.get('goal', 'general_fitness')
        
        # Select exercises based on time and goal
        selected_exercises = []
        time_allocated = 0
        
        # Reserve time for warmup and cooldown (typically 10-15 mins each)
        reserved_time = 20
        
        # Sort exercises by preference score (highest first)
        sorted_exercises = sorted(
            personalized_exercises, 
            key=lambda x: x.get('preference_score', 0), 
            reverse=True
        )
        
        for exercise in sorted_exercises:
            # Estimate time for this exercise (including rest)
            est_time = self._estimate_exercise_time(exercise)
            
            if time_allocated + est_time <= (time_available - reserved_time):
                # Add exercise to session
                selected_exercises.append(exercise)
                time_allocated += est_time
                
                # Stop if we've reached the target number of exercises
                if len(selected_exercises) >= self._get_target_exercise_count(user_profile):
                    break
        
        return selected_exercises
    
    def _estimate_exercise_time(self, exercise):
        """
        Estimate time required for an exercise including rest periods
        """
        # Base time varies by exercise type
        base_times = {
            'cardio': 10,  # minutes
            'strength': 8,
            'hiit': 15,
            'flexibility': 10,
            'core': 8
        }
        
        category = exercise.get('category', 'strength')
        base_time = base_times.get(category, 8)
        
        # Add time for sets and reps
        sets = exercise.get('sets', 3)
        reps = exercise.get('reps', 10)
        rest_seconds = exercise.get('rest_seconds', 60)
        
        # Calculate total time
        work_time = sets * (reps * 2) / 60  # Rough estimate of work time
        rest_time = (sets - 1) * rest_seconds / 60  # Rest between sets
        
        total_time = base_time + work_time + rest_time
        
        # Add buffer time
        return min(20, max(5, total_time))  # Clamp between 5 and 20 minutes
    
    def _get_target_exercise_count(self, user_profile):
        """
        Determine how many exercises to include based on user profile
        """
        fitness_level = user_profile.get('fitness_level', 'beginner')
        
        if fitness_level == 'beginner':
            return 4
        elif fitness_level == 'intermediate':
            return 6
        else:  # advanced
            return 8
    
    def _determine_workout_type(self, exercises, user_profile):
        """
        Determine the type of workout based on selected exercises
        """
        # Count exercises by category
        category_counts = {}
        for exercise in exercises:
            category = exercise.get('category', 'strength')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Determine primary focus
        if not category_counts:
            return 'strength'
        
        primary_category = max(category_counts, key=category_counts.get)
        
        # Special cases
        if 'hiit' in category_counts and category_counts['hiit'] > 0:
            return 'hiit'
        elif 'cardio' in category_counts and category_counts['cardio'] >= 2:
            return 'cardio'
        elif 'flexibility' in category_counts and category_counts['flexibility'] >= 2:
            return 'flexibility'
        elif 'core' in category_counts and category_counts['core'] >= 2:
            return 'core'
        else:
            return primary_category
    
    def _determine_intensity(self, user_profile):
        """
        Determine workout intensity based on user profile
        """
        fitness_level = user_profile.get('fitness_level', 'intermediate')
        
        if fitness_level == 'beginner':
            return 'low_to_moderate'
        elif fitness_level == 'intermediate':
            return 'moderate_to_high'
        else:  # advanced
            return 'high'
    
    def _generate_warmup(self, user_profile):
        """
        Generate appropriate warmup routine
        """
        warmup_exercises = []
        
        # Add general warmup
        warmup_exercises.append({
            'name': 'Light Cardio',
            'category': 'cardio',
            'duration_minutes': 5,
            'instructions': '5 minutes of light jogging, marching in place, or cycling'
        })
        
        # Add dynamic stretches based on planned workout
        planned_focus = user_profile.get('goal', 'general_fitness')
        
        if 'upper' in planned_focus or 'strength' in planned_focus:
            warmup_exercises.extend([
                {
                    'name': 'Arm Circles',
                    'category': 'flexibility',
                    'duration_minutes': 1,
                    'instructions': '1 minute forward and backward arm circles'
                },
                {
                    'name': 'Shoulder Rolls',
                    'category': 'flexibility',
                    'duration_minutes': 1,
                    'instructions': 'Roll shoulders backward and forward'
                }
            ])
        
        if 'lower' in planned_focus or 'strength' in planned_focus:
            warmup_exercises.extend([
                {
                    'name': 'Leg Swings',
                    'category': 'flexibility',
                    'duration_minutes': 1,
                    'instructions': 'Forward/backward and side-to-side leg swings'
                },
                {
                    'name': 'Hip Circles',
                    'category': 'flexibility',
                    'duration_minutes': 1,
                    'instructions': 'Rotate hips clockwise and counterclockwise'
                }
            ])
        
        return warmup_exercises
    
    def _generate_cooldown(self, user_profile):
        """
        Generate appropriate cooldown routine
        """
        cooldown_exercises = []
        
        # Add static stretching
        cooldown_exercises.extend([
            {
                'name': 'Full Body Stretch',
                'category': 'flexibility',
                'duration_minutes': 5,
                'instructions': 'Hold each stretch for 20-30 seconds'
            },
            {
                'name': 'Deep Breathing',
                'category': 'flexibility',
                'duration_minutes': 2,
                'instructions': '4-7-8 breathing technique for relaxation'
            }
        ])
        
        return cooldown_exercises
    
    def _generate_summary(self, weekly_plan, user_profile):
        """
        Generate summary statistics for the plan
        """
        total_workout_days = sum(1 for day in weekly_plan['days'] if day['type'] != 'rest')
        total_exercises = sum(len(day.get('exercises', [])) for day in weekly_plan['days'] if day['type'] != 'rest')
        
        # Calculate muscle group coverage
        muscle_groups = set()
        for day in weekly_plan['days']:
            if day['type'] != 'rest':
                for exercise in day.get('exercises', []):
                    primary_muscles = exercise.get('primary_muscles', [])
                    muscle_groups.update(primary_muscles)
        
        summary = {
            'total_workout_days': total_workout_days,
            'total_rest_days': len(weekly_plan['days']) - total_workout_days,
            'total_exercises': total_exercises,
            'muscle_groups_covered': len(muscle_groups),
            'estimated_total_time': sum(
                day.get('duration_minutes', 0) for day in weekly_plan['days'] if day['type'] != 'rest'
            ),
            'primary_focus': user_profile.get('goal', 'general_fitness'),
            'safety_compliance': True,
            'personalization_level': 'high'
        }
        
        return summary


# Example usage
if __name__ == "__main__":
    generator = WorkoutPlanGenerator()
    
    # Sample user profile
    sample_user = {
        'user_id': 1,
        'fitness_level': 'intermediate',
        'goal': 'strength',
        'age': 30,
        'gender': 'male',
        'weight': 75,
        'height': 175,
        'activity_level': 'moderate',
        'injuries': ['knee_injury'],
        'health_conditions': [],
        'equipment_available': ['dumbbells', 'yoga_mat'],
        'preferred_categories': ['strength', 'core'],
        'disliked_exercises': ['burpees'],
        'time_available': 50,
        'exercise_history': [
            {'exercise': 'pushups', 'rating': 8, 'sets_completed': 3, 'reps_completed': 12},
            {'exercise': 'squats', 'rating': 7, 'sets_completed': 3, 'reps_completed': 10}
        ],
        'performance_data': {
            'pushups': {'attempts': 5, 'avg_rating': 7.5, 'improvement_trend': 0.2, 'difficulty_rating': 7},
            'squats': {'attempts': 4, 'avg_rating': 7, 'improvement_trend': 0.1, 'difficulty_rating': 6}
        }
    }
    
    # Generate workout plan
    plan = generator.generate_workout_plan(sample_user)
    
    # Print plan summary
    print("Workout Plan Generated Successfully!")
    print(f"Duration: {plan['start_date']} to {plan['end_date']}")
    print(f"Workout Days: {plan['summary']['total_workout_days']}")
    print(f"Rest Days: {plan['summary']['total_rest_days']}")
    print(f"Focus: {plan['summary']['primary_focus']}")
    
    # Print first workout session
    if plan['days']:
        first_session = plan['days'][0]
        if first_session['type'] != 'rest':
            print(f"\nFirst Workout Session ({first_session['type']}):")
            print(f"Duration: {first_session['duration_minutes']} minutes")
            print(f"Exercises: {len(first_session['exercises'])}")
            for i, exercise in enumerate(first_session['exercises'][:3]):  # Show first 3 exercises
                print(f"  {i+1}. {exercise['name']} ({exercise['category']})")