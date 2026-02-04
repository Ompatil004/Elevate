"""
Synthetic Data Generator for Fitness and Meal Planner
Generates realistic user behavior patterns for ML model bootstrapping
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os


class SyntheticDataGenerator:
    """
    Generates synthetic user behavior data for ML model bootstrapping
    Following ethical guidelines - no optimal solutions, no guaranteed results
    """
    
    def __init__(self, num_users: int = 100):
        self.num_users = num_users
        self.users = []
        self.workout_behaviors = []
        self.meal_behaviors = []
        
        # Define realistic user characteristics by experience level
        self.user_profiles_by_level = {
            'beginner': {
                'age_range': (18, 45),
                'weight_range': (50, 120),
                'height_range': (150, 190),
                'equipment_likelihood': {
                    'none': 0.6,
                    'yoga_mat': 0.7,
                    'resistance_bands': 0.4,
                    'dumbbells': 0.3,
                    'kettlebell': 0.2
                },
                'workout_completion_rate': 0.6,  # 60% completion rate
                'meal_adherence_rate': 0.5,      # 50% adherence rate
                'perceived_difficulty': ['easy', 'moderate'],  # Beginners find most things moderate/easy
                'fatigue_level': ['low', 'medium'],  # Lower fatigue levels
                'enjoyment_level': ['medium', 'high']  # Generally positive
            },
            'intermediate': {
                'age_range': (20, 55),
                'weight_range': (50, 110),
                'height_range': (155, 195),
                'equipment_likelihood': {
                    'none': 0.2,
                    'yoga_mat': 0.9,
                    'resistance_bands': 0.7,
                    'dumbbells': 0.8,
                    'kettlebell': 0.5,
                    'pullup_bar': 0.3
                },
                'workout_completion_rate': 0.8,  # 80% completion rate
                'meal_adherence_rate': 0.7,      # 70% adherence rate
                'perceived_difficulty': ['moderate', 'hard'],  # Intermediate find things moderate/hard
                'fatigue_level': ['medium', 'high'],  # Medium to high fatigue
                'enjoyment_level': ['medium', 'high']  # Generally positive
            },
            'advanced': {
                'age_range': (22, 60),
                'weight_range': (55, 100),
                'height_range': (160, 195),
                'equipment_likelihood': {
                    'none': 0.05,
                    'yoga_mat': 0.95,
                    'resistance_bands': 0.8,
                    'dumbbells': 0.95,
                    'kettlebell': 0.8,
                    'pullup_bar': 0.6,
                    'exercise_bike': 0.4,
                    'treadmill': 0.3
                },
                'workout_completion_rate': 0.9,  # 90% completion rate
                'meal_adherence_rate': 0.85,     # 85% adherence rate
                'perceived_difficulty': ['hard'],  # Advanced find most things hard
                'fatigue_level': ['high'],         # Higher fatigue levels
                'enjoyment_level': ['medium', 'high']  # Generally positive
            }
        }
    
    def generate_users(self) -> List[Dict[str, Any]]:
        """Generate synthetic user profiles"""
        users = []
        
        for i in range(self.num_users):
            # Randomly assign experience level with realistic distribution
            experience_weights = [0.4, 0.4, 0.2]  # 40% beginner, 40% intermediate, 20% advanced
            experience_level = random.choices(['beginner', 'intermediate', 'advanced'], weights=experience_weights)[0]
            
            profile_config = self.user_profiles_by_level[experience_level]
            
            # Generate user characteristics based on experience level
            user = {
                "user_id": str(uuid.uuid4()),
                "timestamp": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
                "age": random.randint(*profile_config['age_range']),
                "weight": round(random.uniform(*profile_config['weight_range']), 1),
                "height": round(random.uniform(*profile_config['height_range']), 1),
                "gender": random.choice(['male', 'female', 'non-binary', 'other']),
                "fitness_goal": random.choice(['fat_loss', 'muscle_gain', 'maintenance', 'general_fitness', 'endurance', 'strength']),
                "experience_level": experience_level,
                "equipment_available": self._select_equipment(profile_config['equipment_likelihood']),
                "dietary_preference": random.choice(['balanced', 'vegetarian', 'vegan', 'pescatarian', 'gluten_free', 'dairy_free', 'keto', 'mediterranean']),
                "allergies_or_constraints": self._select_allergies(),
                "disclaimer_acknowledged": True,
                "consent_given": True
            }
            
            users.append(user)
        
        self.users = users
        return users
    
    def _select_equipment(self, likelihood_dict: Dict[str, float]) -> List[str]:
        """Select equipment based on likelihood for experience level"""
        equipment = []
        for equip, prob in likelihood_dict.items():
            if random.random() < prob:
                equipment.append(equip)
        return equipment
    
    def _select_allergies(self) -> List[str]:
        """Randomly select allergies with realistic distribution"""
        all_allergies = ['nuts', 'dairy', 'gluten', 'shellfish', 'eggs', 'soy', 'wheat']
        # Select 0-2 allergies with decreasing probability
        num_allergies = random.choices([0, 1, 2], weights=[0.7, 0.25, 0.05])[0]
        return random.sample(all_allergies, min(num_allergies, len(all_allergies)))
    
    def generate_workout_behaviors(self, num_behaviors_per_user: int = 10) -> List[Dict[str, Any]]:
        """Generate synthetic workout behavior data"""
        behaviors = []
        
        for user in self.users:
            user_level = user['experience_level']
            profile_config = self.user_profiles_by_level[user_level]
            
            for _ in range(num_behaviors_per_user):
                # Determine if workout was completed based on user level
                completed = random.random() < profile_config['workout_completion_rate']
                
                behavior = {
                    "record_id": str(uuid.uuid4()),
                    "user_id": user['user_id'],
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    "workout_id": f"workout_{random.randint(1, 50)}",
                    "completion_status": "completed" if completed else random.choice(["partially_completed", "skipped", "interrupted"]),
                    "perceived_difficulty": random.choice(profile_config['perceived_difficulty']),
                    "fatigue_level": random.choice(profile_config['fatigue_level']),
                    "recovery_duration": random.choice(['short', 'average', 'long']),
                    "notes": self._generate_random_notes(completed, user_level),
                    "user_experience_feedback": self._generate_experience_feedback(completed, user_level)
                }
                
                behaviors.append(behavior)
        
        self.workout_behaviors = behaviors
        return behaviors
    
    def _generate_random_notes(self, completed: bool, level: str) -> str:
        """Generate realistic notes based on completion and level"""
        if not completed:
            return random.choice([
                "Had to skip due to schedule conflict",
                "Felt too tired today",
                "Not motivated",
                "Equipment not available",
                "Time constraints"
            ])
        else:
            beginner_notes = [
                "Felt good, challenging but manageable",
                "Need to work on form",
                "Energy levels were appropriate",
                "Good introduction to exercise",
                "Feeling sore but accomplished"
            ]
            intermediate_notes = [
                "Solid workout, pushed myself",
                "Good balance of intensity",
                "Energy levels appropriate",
                "Challenging but achievable",
                "Good progress noted"
            ]
            advanced_notes = [
                "Intense session, good effort",
                "Pushed personal limits",
                "High intensity achieved",
                "Challenging as expected",
                "Good training stimulus"
            ]
            
            if level == 'beginner':
                return random.choice(beginner_notes)
            elif level == 'intermediate':
                return random.choice(intermediate_notes)
            else:
                return random.choice(advanced_notes)
    
    def _generate_experience_feedback(self, completed: bool, level: str) -> str:
        """Generate experience feedback based on completion and level"""
        if not completed:
            return random.choice([
                "Will try to reschedule",
                "Need better planning",
                "Motivation was low",
                "Need to adjust schedule",
                "Disappointed but will continue"
            ])
        else:
            positive_feedback = [
                "Enjoyed the workout",
                "Right difficulty level",
                "Good challenge",
                "Felt accomplished",
                "Will repeat this workout",
                "Good variety",
                "Appropriate intensity",
                "Met expectations"
            ]
            return random.choice(positive_feedback)
    
    def generate_meal_behaviors(self, num_behaviors_per_user: int = 7) -> List[Dict[str, Any]]:
        """Generate synthetic meal behavior data"""
        behaviors = []
        
        for user in self.users:
            user_level = user['experience_level']
            profile_config = self.user_profiles_by_level[user_level]
            
            # Get adherence rate for this user level
            adherence_rate = profile_config['meal_adherence_rate']
            
            for _ in range(num_behaviors_per_user):
                # Determine adherence level based on user characteristics
                adherence_val = random.random()
                if adherence_val < adherence_rate * 0.8:  # 80% of adherence rate = followed
                    adherence_level = "followed"
                elif adherence_val < adherence_rate:  # Between 80% and 100% of adherence rate = partial
                    adherence_level = "partial"
                else:  # Above adherence rate = skipped
                    adherence_level = "skipped"
                
                behavior = {
                    "record_id": str(uuid.uuid4()),
                    "user_id": user['user_id'],
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    "meal_id": f"meal_{random.randint(1, 100)}",
                    "adherence_level": adherence_level,
                    "enjoyment_rating": random.choice(profile_config['enjoyment_level'] + ['low']),
                    "satisfaction_level": random.choice(['unsatisfied', 'neutral', 'satisfied', 'very_satisfied']),
                    "hunger_level_after": random.choice(['very_hungry', 'hungry', 'neutral', 'satisfied', 'full', 'very_full']),
                    "notes": self._generate_meal_notes(adherence_level, user['dietary_preference']),
                    "user_experience_feedback": self._generate_meal_feedback(adherence_level)
                }
                
                behaviors.append(behavior)
        
        self.meal_behaviors = behaviors
        return behaviors
    
    def _generate_meal_notes(self, adherence: str, diet_pref: str) -> str:
        """Generate realistic meal notes"""
        if adherence == 'skipped':
            return random.choice([
                "Not hungry",
                "Too busy",
                "Forgot to eat",
                "Social event interfered",
                "Not in the mood for planned meal"
            ])
        elif adherence == 'partial':
            return random.choice([
                "Modified recipe slightly",
                "Ate most but not all",
                "Substituted ingredients",
                "Reduced portion size",
                "Added extra snack"
            ])
        else:  # followed
            return random.choice([
                "Followed recipe exactly",
                "Enjoyed the flavors",
                "Good portion size",
                "Nutritious and satisfying",
                "Met dietary needs",
                f"Good {diet_pref} option"
            ])
    
    def _generate_meal_feedback(self, adherence: str) -> str:
        """Generate meal experience feedback"""
        if adherence == 'skipped':
            return random.choice([
                "Need better meal planning",
                "Should prep meals ahead",
                "Schedule conflicts",
                "Will try harder tomorrow"
            ])
        else:
            return random.choice([
                "Satisfied with choice",
                "Good flavor profile",
                "Met nutritional goals",
                "Will make again",
                "Appropriate for goals",
                "Enjoyed the experience"
            ])
    
    def save_data_to_files(self, output_dir: str = "synthetic_data"):
        """Save generated data to JSON files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save user profiles
        with open(os.path.join(output_dir, "synthetic_user_profiles.json"), 'w') as f:
            json.dump(self.users, f, indent=2)
        
        # Save workout behaviors
        with open(os.path.join(output_dir, "synthetic_workout_behaviors.json"), 'w') as f:
            json.dump(self.workout_behaviors, f, indent=2)
        
        # Save meal behaviors
        with open(os.path.join(output_dir, "synthetic_meal_behaviors.json"), 'w') as f:
            json.dump(self.meal_behaviors, f, indent=2)
        
        print(f"Synthetic data saved to {output_dir}/ directory")
        print(f"Generated {len(self.users)} user profiles")
        print(f"Generated {len(self.workout_behaviors)} workout behaviors")
        print(f"Generated {len(self.meal_behaviors)} meal behaviors")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated data"""
        stats = {
            "total_users": len(self.users),
            "experience_distribution": {},
            "workout_completion_stats": {},
            "meal_adherence_stats": {}
        }
        
        # Experience distribution
        exp_counts = {}
        for user in self.users:
            exp_level = user['experience_level']
            exp_counts[exp_level] = exp_counts.get(exp_level, 0) + 1
        stats["experience_distribution"] = exp_counts
        
        # Workout completion stats
        completion_counts = {}
        for behavior in self.workout_behaviors:
            status = behavior['completion_status']
            completion_counts[status] = completion_counts.get(status, 0) + 1
        stats["workout_completion_stats"] = completion_counts
        
        # Meal adherence stats
        adherence_counts = {}
        for behavior in self.meal_behaviors:
            level = behavior['adherence_level']
            adherence_counts[level] = adherence_counts.get(level, 0) + 1
        stats["meal_adherence_stats"] = adherence_counts
        
        return stats


def main():
    print("Generating synthetic data for ML model bootstrapping...")
    print("="*60)
    
    # Create generator
    generator = SyntheticDataGenerator(num_users=150)  # Generate 150 users for robust dataset
    
    # Generate all data
    print("Generating user profiles...")
    users = generator.generate_users()
    
    print("Generating workout behaviors...")
    workout_behaviors = generator.generate_workout_behaviors(num_behaviors_per_user=8)
    
    print("Generating meal behaviors...")
    meal_behaviors = generator.generate_meal_behaviors(num_behaviors_per_user=7)
    
    # Save to files
    generator.save_data_to_files()
    
    # Print statistics
    stats = generator.get_statistics()
    print("\nGENERATED DATA STATISTICS:")
    print(f"Total Users: {stats['total_users']}")
    print(f"Experience Distribution: {stats['experience_distribution']}")
    print(f"Workout Completion Stats: {stats['workout_completion_stats']}")
    print(f"Meal Adherence Stats: {stats['meal_adherence_stats']}")
    
    print("\nSynthetic data generation complete!")
    print("Data is suitable for ML model bootstrapping.")
    print("No optimal solutions or guaranteed results encoded.")
    print("All data represents user behavior patterns only.")


if __name__ == "__main__":
    main()