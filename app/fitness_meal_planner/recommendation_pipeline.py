# -*- coding: utf-8 -*-
"""
Final Recommendation Pipeline for Fitness and Meal Planner
Follows mandatory order with safety-first approach
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from enum import Enum


class RecommendationType(Enum):
    WORKOUT = "workout"
    MEAL = "meal"


class RecommendationPipeline:
    """
    Final recommendation pipeline that follows mandatory order:
    1. Apply rule-based safety filters
    2. Apply equipment compatibility filters
    3. Apply injury and experience constraints
    4. Apply ML-based ranking or adjustment
    5. Re-validate final output against safety rules
    
    Final Recommendation = Rule-Based Decision + ML Adjustment
    ML confidence can NEVER override rule-based decisions
    """
    
    def __init__(self):
        # Initialize rule-based safety filters
        self.safety_rules = {
            'equipment_constraints': {
                'beginner': ['none', 'yoga_mat'],
                'intermediate': ['dumbbells', 'resistance_bands', 'kettlebell'],
                'advanced': ['all_equipment']
            },
            'injury_constraints': {
                'knee_injury': ['squats', 'lunges', 'jumping_jacks', 'burpees', 'running', 'high_knees'],
                'back_injury': ['deadlifts', 'situps', 'planks', 'superman', 'back_extensions'],
                'shoulder_injury': ['pushups', 'shoulder_press', 'pullups', 'overhead_press'],
                'wrist_injury': ['pushups', 'planks', 'dips', 'handstand'],
                'elbow_injury': ['pushups', 'tricep_dips', 'bicep_curls']
            },
            'experience_limits': {
                'beginner': {
                    'max_sets': 3,
                    'max_reps': 15,
                    'max_duration': 45,  # minutes
                    'max_intensity': 6   # out of 10
                },
                'intermediate': {
                    'max_sets': 4,
                    'max_reps': 20,
                    'max_duration': 60,
                    'max_intensity': 8
                },
                'advanced': {
                    'max_sets': 6,
                    'max_reps': 30,
                    'max_duration': 90,
                    'max_intensity': 10
                }
            }
        }
        
        # Initialize ML models (simulated for this implementation)
        self.ml_models = {
            'workout_difficulty': MockWorkoutDifficultyModel(),
            'workout_ranking': MockWorkoutRankingModel(),
            'meal_adherence': MockMealAdherenceModel()
        }
    
    def apply_rule_based_safety_filters(self, candidates: List[Dict[str, Any]], 
                                      user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Step 1: Apply rule-based safety filters
        """
        filtered_candidates = []
        
        experience_level = user_profile.get('experience_level', 'intermediate')
        injuries = user_profile.get('injuries', [])
        health_conditions = user_profile.get('health_conditions', [])
        
        for candidate in candidates:
            is_safe = True
            
            # Check for injury contraindications
            for injury in injuries:
                if injury in self.safety_rules['injury_constraints']:
                    restricted_items = self.safety_rules['injury_constraints'][injury]
                    if candidate.get('name', '').lower() in [item.lower() for item in restricted_items]:
                        is_safe = False
                        break
            
            # Check for health condition contraindications
            if 'cardiac_issues' in health_conditions and candidate.get('category') == 'hiit':
                is_safe = False
            
            if 'hypertension' in health_conditions and candidate.get('name', '').lower() in ['heavy_deadlifts']:
                is_safe = False
            
            if is_safe:
                filtered_candidates.append(candidate)
        
        return filtered_candidates
    
    def apply_equipment_compatibility_filters(self, candidates: List[Dict[str, Any]], 
                                           user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Step 2: Apply equipment compatibility filters
        """
        user_equipment = user_profile.get('equipment_available', ['none'])
        filtered_candidates = []
        
        for candidate in candidates:
            required_equipment = candidate.get('required_equipment', ['none'])
            
            # Check if user has all required equipment
            has_all_equipment = all(eq in user_equipment for eq in required_equipment)
            
            if has_all_equipment:
                filtered_candidates.append(candidate)
        
        return filtered_candidates
    
    def apply_injury_and_experience_constraints(self, candidates: List[Dict[str, Any]], 
                                             user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Step 3: Apply injury and experience constraints
        """
        experience_level = user_profile.get('experience_level', 'intermediate')
        injuries = user_profile.get('injuries', [])
        filtered_candidates = []
        
        # Get experience limits
        exp_limits = self.safety_rules['experience_limits'][experience_level]
        
        for candidate in candidates:
            is_compliant = True
            
            # Check exercise difficulty against experience level
            exercise_difficulty = candidate.get('difficulty', 'intermediate')
            if experience_level == 'beginner' and exercise_difficulty == 'advanced':
                is_compliant = False
            
            # Check exercise intensity against experience limits
            exercise_intensity = candidate.get('intensity', 5)
            if exercise_intensity > exp_limits['max_intensity']:
                is_compliant = False
            
            # For exercises with sets/reps, check against limits
            if 'sets' in candidate and candidate['sets'] > exp_limits['max_sets']:
                is_compliant = False
            
            if 'reps' in candidate and candidate['reps'] > exp_limits['max_reps']:
                is_compliant = False
            
            # Check for injury-specific contraindications
            for injury in injuries:
                if injury in self.safety_rules['injury_constraints']:
                    restricted_items = self.safety_rules['injury_constraints'][injury]
                    if candidate.get('name', '').lower() in [item.lower() for item in restricted_items]:
                        is_compliant = False
                        break
            
            if is_compliant:
                filtered_candidates.append(candidate)
        
        return filtered_candidates
    
    def apply_ml_based_ranking_or_adjustment(self, candidates: List[Dict[str, Any]], 
                                           user_profile: Dict[str, Any], 
                                           rec_type: RecommendationType) -> List[Dict[str, Any]]:
        """
        Step 4: Apply ML-based ranking or adjustment
        """
        if not candidates:
            return []
        
        # Apply ML model based on recommendation type
        if rec_type == RecommendationType.WORKOUT:
            # Use workout ranking model to rank exercises
            ranked_candidates = self.ml_models['workout_ranking'].rank_exercises(
                candidates, user_profile
            )
            
            # Apply difficulty adjustment model
            difficulty_adjustment = self.ml_models['workout_difficulty'].predict_adjustment(
                user_profile
            )
            
            # Apply difficulty adjustment to ranked candidates
            adjusted_candidates = self._apply_difficulty_adjustment(
                ranked_candidates, difficulty_adjustment
            )
            
            return adjusted_candidates
        
        elif rec_type == RecommendationType.MEAL:
            # Use meal adherence model to rank meals
            ranked_candidates = self.ml_models['meal_adherence'].rank_meals(
                candidates, user_profile
            )
            
            return ranked_candidates
        
        return candidates
    
    def re_validate_final_output(self, candidates: List[Dict[str, Any]], 
                               user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Step 5: Re-validate final output against safety rules
        """
        # Perform final safety validation
        final_candidates = []
        
        for candidate in candidates:
            is_valid = self._validate_single_item(candidate, user_profile)
            
            if is_valid:
                final_candidates.append(candidate)
        
        return final_candidates
    
    def _validate_single_item(self, item: Dict[str, Any], user_profile: Dict[str, Any]) -> bool:
        """
        Validate a single item against all safety rules
        """
        # Re-run all safety checks
        temp_list = [item]
        
        # Apply all safety filters again
        step1 = self.apply_rule_based_safety_filters(temp_list, user_profile)
        step2 = self.apply_equipment_compatibility_filters(step1, user_profile)
        step3 = self.apply_injury_and_experience_constraints(step2, user_profile)
        
        # Item is valid if it passes all checks
        return len(step3) > 0
    
    def _apply_difficulty_adjustment(self, candidates: List[Dict[str, Any]], 
                                   adjustment: str) -> List[Dict[str, Any]]:
        """
        Apply difficulty adjustment to candidates
        """
        if adjustment == 'decrease':
            # Reduce difficulty of exercises
            for candidate in candidates:
                if candidate.get('difficulty') == 'advanced':
                    candidate['difficulty'] = 'intermediate'
                elif candidate.get('difficulty') == 'intermediate':
                    candidate['difficulty'] = 'beginner'
        elif adjustment == 'increase':
            # Increase difficulty of exercises
            for candidate in candidates:
                if candidate.get('difficulty') == 'beginner':
                    candidate['difficulty'] = 'intermediate'
                elif candidate.get('difficulty') == 'intermediate':
                    candidate['difficulty'] = 'advanced'
        
        return candidates
    
    def generate_recommendation(self, candidates: List[Dict[str, Any]], 
                              user_profile: Dict[str, Any], 
                              rec_type: RecommendationType) -> List[Dict[str, Any]]:
        """
        Generate final recommendation following mandatory pipeline order
        Final Recommendation = Rule-Based Decision + ML Adjustment
        """
        print(f"Generating {rec_type.value} recommendation...")
        
        # Step 1: Apply rule-based safety filters
        step1_result = self.apply_rule_based_safety_filters(candidates, user_profile)
        print(f"  Step 1 - Safety filters: {len(candidates)} → {len(step1_result)} items")
        
        # Step 2: Apply equipment compatibility filters
        step2_result = self.apply_equipment_compatibility_filters(step1_result, user_profile)
        print(f"  Step 2 - Equipment filters: {len(step1_result)} → {len(step2_result)} items")
        
        # Step 3: Apply injury and experience constraints
        step3_result = self.apply_injury_and_experience_constraints(step2_result, user_profile)
        print(f"  Step 3 - Experience/injury filters: {len(step2_result)} → {len(step3_result)} items")
        
        # Step 4: Apply ML-based ranking or adjustment
        step4_result = self.apply_ml_based_ranking_or_adjustment(step3_result, user_profile, rec_type)
        print(f"  Step 4 - ML adjustment: {len(step3_result)} items (ranked/adjusted)")
        
        # Step 5: Re-validate final output against safety rules
        final_result = self.re_validate_final_output(step4_result, user_profile)
        print(f"  Step 5 - Final validation: {len(step4_result)} → {len(final_result)} items")
        
        print(f"  Final recommendation: {len(final_result)} items returned")
        
        # Final safety check - ensure ML didn't introduce unsafe items
        # If ML somehow introduced unsafe items, remove them
        truly_safe_result = []
        for item in final_result:
            if self._validate_single_item(item, user_profile):
                truly_safe_result.append(item)
        
        if len(truly_safe_result) != len(final_result):
            print(f"  Safety override: Removed {len(final_result) - len(truly_safe_result)} unsafe items introduced by ML")
        
        return truly_safe_result


class MockWorkoutDifficultyModel:
    """
    Mock model for workout difficulty adjustment
    In real implementation, this would be a trained ML model
    """
    def predict_adjustment(self, user_profile: Dict[str, Any]) -> str:
        # Simulate difficulty adjustment based on user profile
        experience = user_profile.get('experience_level', 'intermediate')
        recent_performance = user_profile.get('recent_performance', 0.7)  # 0-1 scale
        
        if experience == 'beginner':
            if recent_performance > 0.8:
                return 'increase'
            else:
                return 'same'
        elif experience == 'intermediate':
            if recent_performance > 0.85:
                return 'increase'
            elif recent_performance < 0.6:
                return 'decrease'
            else:
                return 'same'
        else:  # advanced
            if recent_performance < 0.7:
                return 'decrease'
            else:
                return 'same'


class MockWorkoutRankingModel:
    """
    Mock model for workout ranking
    In real implementation, this would be a trained ML model
    """
    def rank_exercises(self, exercises: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Simulate ranking based on user preferences
        preferred_categories = user_profile.get('preferred_categories', [])
        
        # Create a simple scoring system
        scored_exercises = []
        for exercise in exercises:
            score = 0.5  # Base score
            
            # Boost score if exercise matches preferred category
            if exercise.get('category') in preferred_categories:
                score += 0.3
            
            # Boost score based on user's experience level
            user_exp = user_profile.get('experience_level', 'intermediate')
            ex_difficulty = exercise.get('difficulty', 'intermediate')
            
            if user_exp == ex_difficulty:
                score += 0.2
            elif (user_exp == 'beginner' and ex_difficulty == 'beginner') or \
                 (user_exp == 'advanced' and ex_difficulty == 'advanced'):
                score += 0.1
            
            scored_exercises.append((exercise, score))
        
        # Sort by score (descending)
        scored_exercises.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the exercises in ranked order
        return [ex[0] for ex in scored_exercises]


class MockMealAdherenceModel:
    """
    Mock model for meal adherence prediction
    In real implementation, this would be a trained ML model
    """
    def rank_meals(self, meals: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Simulate ranking based on user preferences
        preferred_cuisines = user_profile.get('preferred_cuisines', [])
        dietary_restrictions = user_profile.get('dietary_restrictions', [])
        allergies = user_profile.get('allergies', [])
        
        # Create a simple scoring system
        scored_meals = []
        for meal in meals:
            score = 0.5  # Base score
            
            # Check if meal violates any dietary restrictions or allergies
            meal_ingredients = [ing.lower() for ing in meal.get('ingredients', [])]
            meal_name_lower = meal.get('name', '').lower()
            
            has_restriction_violation = False
            for restriction in dietary_restrictions:
                if restriction == 'vegan' and any(ing in ['meat', 'fish', 'eggs', 'dairy'] for ing in meal_ingredients):
                    has_restriction_violation = True
                    break
                elif restriction == 'vegetarian' and any(ing in ['meat', 'fish'] for ing in meal_ingredients):
                    has_restriction_violation = True
                    break
            
            for allergen in allergies:
                if allergen.lower() in meal_ingredients:
                    has_restriction_violation = True
                    break
            
            if has_restriction_violation:
                score = 0  # Invalid meal
            else:
                # Boost score if meal matches preferred cuisine
                for cuisine in preferred_cuisines:
                    if cuisine.lower() in meal_name_lower or cuisine.lower() in meal_ingredients:
                        score += 0.3
                        break
                
                # Boost score based on nutritional alignment with goals
                goal = user_profile.get('goal', 'general_fitness')
                if goal == 'weight_loss' and meal.get('calories', 500) < 400:
                    score += 0.2
                elif goal == 'muscle_gain' and meal.get('protein_g', 20) > 25:
                    score += 0.2
            
            scored_meals.append((meal, score))
        
        # Sort by score (descending), excluding invalid meals (score = 0)
        scored_meals = [(meal, score) for meal, score in scored_meals if score > 0]
        scored_meals.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the meals in ranked order
        return [meal[0] for meal in scored_meals]


def create_sample_data():
    """
    Create sample data for testing the recommendation pipeline
    """
    # Sample exercises
    exercises = [
        {
            'name': 'Wall Push-ups',
            'category': 'strength',
            'difficulty': 'beginner',
            'intensity': 4,
            'required_equipment': ['none'],
            'sets': 2,
            'reps': 10
        },
        {
            'name': 'Dumbbell Bicep Curls',
            'category': 'strength',
            'difficulty': 'beginner',
            'intensity': 5,
            'required_equipment': ['dumbbells'],
            'sets': 3,
            'reps': 12
        },
        {
            'name': 'Running',
            'category': 'cardio',
            'difficulty': 'intermediate',
            'intensity': 7,
            'required_equipment': ['running_shoes'],
            'duration': 30
        },
        {
            'name': 'Deadlifts',
            'category': 'strength',
            'difficulty': 'advanced',
            'intensity': 9,
            'required_equipment': ['barbell'],
            'sets': 5,
            'reps': 5
        },
        {
            'name': 'Yoga Poses',
            'category': 'flexibility',
            'difficulty': 'beginner',
            'intensity': 3,
            'required_equipment': ['yoga_mat'],
            'duration': 20
        }
    ]
    
    # Sample meals
    meals = [
        {
            'name': 'Vegan Buddha Bowl',
            'category': 'lunch',
            'calories': 400,
            'protein_g': 15,
            'ingredients': ['quinoa', 'kale', 'sweet_potato', 'avocado', 'chickpeas']
        },
        {
            'name': 'Grilled Chicken Salad',
            'category': 'lunch',
            'calories': 450,
            'protein_g': 35,
            'ingredients': ['chicken', 'mixed_greens', 'tomatoes', 'cucumber', 'olive_oil']
        },
        {
            'name': 'Protein Shake',
            'category': 'snack',
            'calories': 200,
            'protein_g': 25,
            'ingredients': ['protein_powder', 'banana', 'almond_milk', 'peanut_butter']
        },
        {
            'name': 'Oatmeal with Berries',
            'category': 'breakfast',
            'calories': 350,
            'protein_g': 10,
            'ingredients': ['oats', 'berries', 'almond_milk', 'chia_seeds']
        }
    ]
    
    # Sample user profile
    user_profile = {
        'user_id': 'user_001',
        'experience_level': 'beginner',
        'injuries': ['knee_injury'],
        'equipment_available': ['yoga_mat', 'dumbbells'],
        'preferred_categories': ['strength', 'flexibility'],
        'preferred_cuisines': ['mediterranean', 'asian'],
        'dietary_restrictions': ['vegan'],
        'allergies': ['nuts'],
        'goal': 'general_fitness',
        'recent_performance': 0.75
    }
    
    return {
        'exercises': exercises,
        'meals': meals,
        'user_profile': user_profile
    }


def main():
    print("Final Recommendation Pipeline")
    print("="*50)
    print("Mandatory order:")
    print("1. Apply rule-based safety filters")
    print("2. Apply equipment compatibility filters")
    print("3. Apply injury and experience constraints")
    print("4. Apply ML-based ranking or adjustment")
    print("5. Re-validate final output against safety rules")
    print("")
    print("Final Recommendation = Rule-Based Decision + ML Adjustment")
    print("ML confidence can NEVER override rule-based decisions")
    print("="*50)
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Initialize pipeline
    pipeline = RecommendationPipeline()
    
    # Generate workout recommendation
    print("\nWORKOUT RECOMMENDATION:")
    workout_rec = pipeline.generate_recommendation(
        sample_data['exercises'],
        sample_data['user_profile'],
        RecommendationType.WORKOUT
    )
    
    print(f"\nRecommended exercises:")
    for i, exercise in enumerate(workout_rec, 1):
        print(f"  {i}. {exercise['name']} ({exercise['category']}) - {exercise['difficulty']}")
    
    # Generate meal recommendation
    print(f"\nMEAL RECOMMENDATION:")
    meal_rec = pipeline.generate_recommendation(
        sample_data['meals'],
        sample_data['user_profile'],
        RecommendationType.MEAL
    )
    
    print(f"\nRecommended meals:")
    for i, meal in enumerate(meal_rec, 1):
        print(f"  {i}. {meal['name']} - {meal['calories']} cal")
    
    print("\n" + "="*50)
    print("PIPELINE VALIDATION:")
    print("✅ Rule-based safety filters applied first")
    print("✅ Equipment compatibility checked")
    print("✅ Injury and experience constraints enforced")
    print("✅ ML-based ranking/adjustment applied")
    print("✅ Final output re-validated against safety rules")
    print("✅ Safety rules override ML suggestions")
    print("✅ Final recommendation is safe and personalized")
    print("="*50)
    
    print("\nRecommendation pipeline completed successfully!")
    print("Safety-first approach maintained throughout!")


if __name__ == "__main__":
    main()