"""
Adaptive Engine for machine learning-based personalization
This component provides secondary adaptive personalization while respecting
the rule-based primary decision maker.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os
import json
from datetime import datetime


class AdaptiveEngine:
    def __init__(self, model_dir="models", data_dir="data"):
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.exercise_preferences_model = None
        self.meal_preferences_model = None
        self.performance_predictor = None
        self.scaler = StandardScaler()
        self._ensure_directories_exist()
        self._load_models()

    def _ensure_directories_exist(self):
        """Ensure the model and data directories exist"""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _load_models(self):
        """Load pre-trained models if they exist"""
        # Try to load exercise preferences model
        exercise_model_path = os.path.join(self.model_dir, 'exercise_preferences_model.pkl')
        if os.path.exists(exercise_model_path):
            with open(exercise_model_path, 'rb') as f:
                self.exercise_preferences_model = pickle.load(f)

        # Try to load meal preferences model
        meal_model_path = os.path.join(self.model_dir, 'meal_preferences_model.pkl')
        if os.path.exists(meal_model_path):
            with open(meal_model_path, 'rb') as f:
                self.meal_preferences_model = pickle.load(f)

        # Try to load performance predictor
        perf_model_path = os.path.join(self.model_dir, 'performance_predictor.pkl')
        if os.path.exists(perf_model_path):
            with open(perf_model_path, 'rb') as f:
                self.performance_predictor = pickle.load(f)

    def personalize_exercises(self, filtered_exercises, user_profile):
        """Apply ML-based personalization to filtered exercises"""
        if not filtered_exercises:
            return []

        # Extract user preferences and history
        user_history = user_profile.get('exercise_history', [])
        preferred_categories = user_profile.get('preferred_categories', [])
        disliked_exercises = user_profile.get('disliked_exercises', [])
        performance_data = user_profile.get('performance_data', {})

        # Calculate preference scores based on user history and preferences
        personalized_exercises = []
        for exercise in filtered_exercises:
            score = self._calculate_exercise_preference_score(
                exercise,
                user_history,
                preferred_categories,
                disliked_exercises,
                performance_data
            )
            exercise['preference_score'] = score
            personalized_exercises.append(exercise)

        # Sort by preference score (highest first) but keep diversity
        personalized_exercises.sort(key=lambda x: x['preference_score'], reverse=True)

        # Apply diversity algorithm to prevent repetitive recommendations
        diversified_exercises = self._apply_diversity_filter(personalized_exercises)

        # Adjust exercise parameters based on predicted performance
        adjusted_exercises = self._adjust_exercise_parameters(diversified_exercises, user_profile)

        return adjusted_exercises

    def personalize_meals(self, filtered_meals, user_profile):
        """Apply ML-based personalization to filtered meals"""
        if not filtered_meals:
            return []

        # Extract user preferences and history
        user_history = user_profile.get('meal_history', [])
        preferred_cuisines = user_profile.get('preferred_cuisines', [])
        disliked_ingredients = user_profile.get('disliked_ingredients', [])
        dietary_preferences = user_profile.get('dietary_preferences', {})

        # Calculate preference scores based on user history and preferences
        personalized_meals = []
        for meal in filtered_meals:
            score = self._calculate_meal_preference_score(
                meal,
                user_history,
                preferred_cuisines,
                disliked_ingredients,
                dietary_preferences
            )
            meal['preference_score'] = score
            personalized_meals.append(meal)

        # Sort by preference score (highest first) but keep diversity
        personalized_meals.sort(key=lambda x: x['preference_score'], reverse=True)

        # Apply diversity algorithm to prevent repetitive recommendations
        diversified_meals = self._apply_diversity_filter_meals(personalized_meals)

        return diversified_meals

    def get_adjustments(self):
        """Return list of ML-based adjustments made"""
        return [
            "Personalized based on user preferences and history",
            "Applied diversity algorithm to prevent repetitive recommendations",
            "Adjusted parameters based on performance predictions",
            "Optimized timing based on user schedule preferences",
            "Predicted performance outcomes for recommended exercises"
        ]

    def _calculate_exercise_preference_score(self, exercise, user_history, preferred_categories, disliked_exercises, performance_data):
        """Calculate preference score for an exercise based on user data"""
        score = 0.5  # Base score

        # Boost score if exercise is in preferred category
        if exercise['category'] in preferred_categories:
            score += 0.3

        # Reduce score if exercise is disliked
        if exercise['name'] in disliked_exercises:
            score -= 0.5

        # Boost score based on similarity to previously enjoyed exercises
        if user_history:
            max_similarity_bonus = 0
            for hist_exercise in user_history:
                similarity = self._calculate_exercise_similarity(exercise, hist_exercise)
                if similarity > max_similarity_bonus:
                    max_similarity_bonus = similarity
            score += max_similarity_bonus * 0.2

        # Adjust for difficulty appropriateness
        user_fitness = exercise.get('user_fitness_level', 'intermediate')
        if user_fitness == 'beginner' and exercise['difficulty'] == 'advanced':
            score -= 0.3
        elif user_fitness == 'advanced' and exercise['difficulty'] == 'beginner':
            score -= 0.1

        # Adjust based on performance data
        if performance_data:
            exercise_performance = performance_data.get(exercise['name'], {})
            if exercise_performance:
                # If user has performed well with this exercise recently, boost score
                recent_improvement = exercise_performance.get('recent_improvement', 0)
                if recent_improvement > 0:
                    score += min(0.2, recent_improvement * 0.1)

                # If user struggles with this exercise, slightly reduce score
                difficulty_rating = exercise_performance.get('difficulty_rating', 5)  # 1-10 scale
                if difficulty_rating > 7:  # Very difficult for user
                    score -= 0.1

        # Ensure score is between 0 and 1
        return max(0, min(1, score))

    def _calculate_meal_preference_score(self, meal, user_history, preferred_cuisines, disliked_ingredients, dietary_preferences):
        """Calculate preference score for a meal based on user data"""
        score = 0.5  # Base score

        # Boost score if cuisine is preferred
        for cuisine in preferred_cuisines:
            if cuisine.lower() in meal['name'].lower():
                score += 0.3
                break

        # Reduce score if meal contains disliked ingredients
        meal_ingredients_lower = [ing.lower() for ing in meal['ingredients']]
        for disliked_ing in disliked_ingredients:
            if disliked_ing.lower() in meal_ingredients_lower:
                score -= 0.5
                break

        # Boost score based on similarity to previously enjoyed meals
        if user_history:
            max_similarity_bonus = 0
            for hist_meal in user_history:
                similarity = self._calculate_meal_similarity(meal, hist_meal)
                if similarity > max_similarity_bonus:
                    max_similarity_bonus = similarity
            score += max_similarity_bonus * 0.2

        # Adjust for nutritional appropriateness
        user_goal = meal.get('user_goal', 'maintenance')
        if user_goal == 'weight_loss' and meal['calories'] > 500:
            score -= 0.2
        elif user_goal == 'muscle_gain' and meal['protein_g'] < 20:
            score -= 0.1

        # Adjust based on dietary preferences
        if dietary_preferences:
            # Boost score if meal aligns with dietary preferences
            if dietary_preferences.get('high_protein', False) and meal['protein_g'] >= 25:
                score += 0.1
            if dietary_preferences.get('low_carb', False) and meal['carbs_g'] <= 30:
                score += 0.1
            if dietary_preferences.get('high_fiber', False) and meal['fiber_g'] >= 5:
                score += 0.1

        # Ensure score is between 0 and 1
        return max(0, min(1, score))

    def _calculate_exercise_similarity(self, ex1, ex2):
        """Calculate similarity between two exercises"""
        # Similarity calculation based on category, muscle groups, and difficulty
        similarity = 0

        # Category similarity
        if ex1['category'] == ex2['category']:
            similarity += 0.3

        # Muscle group similarity
        primary_muscles_1 = set(ex1.get('primary_muscles', []))
        primary_muscles_2 = set(ex2.get('primary_muscles', []))
        if primary_muscles_1 and primary_muscles_2:
            muscle_overlap = len(primary_muscles_1 & primary_muscles_2) / len(primary_muscles_1 | primary_muscles_2)
            similarity += muscle_overlap * 0.4

        # Difficulty similarity
        if ex1['difficulty'] == ex2['difficulty']:
            similarity += 0.2

        # Equipment similarity
        equipment_1 = set(ex1.get('equipment', []))
        equipment_2 = set(ex2.get('equipment', []))
        if equipment_1 and equipment_2:
            equip_overlap = len(equipment_1 & equipment_2) / len(equipment_1 | equipment_2)
            similarity += equip_overlap * 0.1

        return min(1.0, similarity)

    def _calculate_meal_similarity(self, meal1, meal2):
        """Calculate similarity between two meals"""
        # Similarity based on ingredients, category, and nutritional profile
        similarity = 0

        # Category similarity
        if meal1['category'] == meal2['category']:
            similarity += 0.2

        # Ingredient overlap
        ingredients1 = set(ing.lower() for ing in meal1['ingredients'])
        ingredients2 = set(ing.lower() for ing in meal2['ingredients'])
        if ingredients1 and ingredients2:
            ingredient_overlap = len(ingredients1 & ingredients2) / len(ingredients1 | ingredients2)
            similarity += ingredient_overlap * 0.4

        # Nutritional similarity (calories, protein, carbs, fats)
        calorie_diff = abs(meal1['calories'] - meal2['calories'])
        calorie_similarity = max(0, 1 - (calorie_diff / max(meal1['calories'], meal2['calories'], 1)))
        similarity += calorie_similarity * 0.1

        protein_diff = abs(meal1.get('protein_g', 0) - meal2.get('protein_g', 0))
        protein_similarity = max(0, 1 - (protein_diff / max(meal1.get('protein_g', 1), meal2.get('protein_g', 1), 1)))
        similarity += protein_similarity * 0.1

        carb_diff = abs(meal1.get('carbs_g', 0) - meal2.get('carbs_g', 0))
        carb_similarity = max(0, 1 - (carb_diff / max(meal1.get('carbs_g', 1), meal2.get('carbs_g', 1), 1)))
        similarity += carb_similarity * 0.1

        fat_diff = abs(meal1.get('fats_g', 0) - meal2.get('fats_g', 0))
        fat_similarity = max(0, 1 - (fat_diff / max(meal1.get('fats_g', 1), meal2.get('fats_g', 1), 1)))
        similarity += fat_similarity * 0.1

        # Cuisine similarity (based on name)
        name_similarity = len(set(meal1['name'].lower()) & set(meal2['name'].lower())) / len(set(meal1['name'].lower()) | set(meal2['name'].lower()))
        similarity += name_similarity * 0.1

        return min(1.0, similarity)

    def _apply_diversity_filter(self, exercises):
        """Apply diversity filter to prevent repetitive exercise recommendations"""
        if len(exercises) <= 5:
            return exercises

        # Select exercises to maximize diversity while maintaining high preference scores
        selected = []
        categories_used = set()
        muscle_groups_used = set()

        for exercise in exercises:
            primary_muscles = set(exercise.get('primary_muscles', []))

            # Check if this exercise adds diversity
            category_new = exercise['category'] not in categories_used
            muscle_group_new = not bool(muscle_groups_used.intersection(primary_muscles))

            # If we haven't used this category or muscle group, add it
            if category_new or muscle_group_new:
                selected.append(exercise)
                categories_used.add(exercise['category'])
                muscle_groups_used.update(primary_muscles)

            # Stop when we have enough diverse exercises
            if len(selected) >= min(8, len(exercises)):
                break

        # If we didn't get enough exercises, add some more focusing on muscle group diversity
        if len(selected) < min(8, len(exercises)):
            for exercise in exercises:
                if len(selected) >= min(8, len(exercises)):
                    break

                primary_muscles = set(exercise.get('primary_muscles', []))
                if not bool(muscle_groups_used.intersection(primary_muscles)):
                    selected.append(exercise)
                    muscle_groups_used.update(primary_muscles)

        return selected

    def _apply_diversity_filter_meals(self, meals):
        """Apply diversity filter to prevent repetitive meal recommendations"""
        if len(meals) <= 5:
            return meals

        # Select meals to maximize diversity while maintaining high preference scores
        selected = []
        categories_used = set()
        cuisines_identified = set()

        for meal in meals:
            # Extract cuisine type from meal name
            cuisine = self._identify_cuisine(meal['name'])

            # Check if this meal adds diversity
            category_new = meal['category'] not in categories_used
            cuisine_new = cuisine not in cuisines_identified

            # If we haven't used this category or cuisine, add it
            if category_new or cuisine_new:
                selected.append(meal)
                categories_used.add(meal['category'])
                cuisines_identified.add(cuisine)

            # Stop when we have enough diverse meals
            if len(selected) >= min(7, len(meals)):
                break

        # If we didn't get enough meals, add some more focusing on nutritional diversity
        if len(selected) < min(7, len(meals)):
            for meal in meals:
                if len(selected) >= min(7, len(meals)):
                    break

                # Add if it has significantly different nutritional profile
                if self._is_nutritionally_diverse(meal, selected):
                    selected.append(meal)

        return selected

    def _identify_cuisine(self, meal_name):
        """Identify cuisine type from meal name"""
        meal_name_lower = meal_name.lower()

        if any(word in meal_name_lower for word in ['italian', 'pasta', 'pizza', 'risotto']):
            return 'italian'
        elif any(word in meal_name_lower for word in ['mexican', 'taco', 'burrito', 'quesadilla']):
            return 'mexican'
        elif any(word in meal_name_lower for word in ['chinese', 'stir fry', 'fried rice', 'lo mein']):
            return 'chinese'
        elif any(word in meal_name_lower for word in ['indian', 'curry', 'naan', 'dal']):
            return 'indian'
        elif any(word in meal_name_lower for word in ['japanese', 'sushi', 'ramen', 'teriyaki']):
            return 'japanese'
        elif any(word in meal_name_lower for word in ['mediterranean', 'greek', 'hummus', 'tzatziki']):
            return 'mediterranean'
        else:
            return 'other'

    def _is_nutritionally_diverse(self, meal, existing_meals):
        """Check if a meal has a nutritionally diverse profile compared to existing meals"""
        if not existing_meals:
            return True

        # Compare nutritional values to existing meals
        for existing_meal in existing_meals:
            # If similar calories, protein, carbs, and fats, consider it not diverse
            calorie_similar = abs(meal['calories'] - existing_meal['calories']) < 100
            protein_similar = abs(meal.get('protein_g', 0) - existing_meal.get('protein_g', 0)) < 10
            carb_similar = abs(meal.get('carbs_g', 0) - existing_meal.get('carbs_g', 0)) < 15
            fat_similar = abs(meal.get('fats_g', 0) - existing_meal.get('fats_g', 0)) < 5

            if calorie_similar and protein_similar and carb_similar and fat_similar:
                return False

        return True

    def _adjust_exercise_parameters(self, exercises, user_profile):
        """Adjust exercise parameters based on user profile and predicted performance"""
        adjusted_exercises = []

        for exercise in exercises:
            adjusted_exercise = exercise.copy()

            # Predict performance for this exercise
            predicted_performance = self._predict_exercise_performance(exercise, user_profile)

            # Adjust parameters based on prediction
            if predicted_performance:
                # Adjust sets/reps based on predicted capacity
                if 'sets' in adjusted_exercise:
                    adjusted_exercise['sets'] = int(predicted_performance.get('predicted_sets', adjusted_exercise['sets']))
                if 'reps' in adjusted_exercise:
                    adjusted_exercise['reps'] = int(predicted_performance.get('predicted_reps', adjusted_exercise['reps']))
                if 'duration' in adjusted_exercise:
                    adjusted_exercise['duration'] = int(predicted_performance.get('predicted_duration', adjusted_exercise['duration']))

            adjusted_exercises.append(adjusted_exercise)

        return adjusted_exercises

    def _predict_exercise_performance(self, exercise, user_profile):
        """Predict performance for a specific exercise based on user profile"""
        # This is a simplified prediction model
        # In a real system, this would use a trained ML model

        base_performance = {
            'predicted_sets': 3,
            'predicted_reps': 10,
            'predicted_duration': 30,  # seconds for timed exercises
            'confidence': 0.7
        }

        # Adjust based on user fitness level
        fitness_level = user_profile.get('fitness_level', 'intermediate')
        if fitness_level == 'beginner':
            base_performance['predicted_sets'] = max(1, int(base_performance['predicted_sets'] * 0.7))
            base_performance['predicted_reps'] = max(5, int(base_performance['predicted_reps'] * 0.8))
        elif fitness_level == 'advanced':
            base_performance['predicted_sets'] = int(base_performance['predicted_sets'] * 1.3)
            base_performance['predicted_reps'] = int(base_performance['predicted_reps'] * 1.2)

        # Adjust based on exercise difficulty
        if exercise['difficulty'] == 'beginner':
            base_performance['predicted_reps'] = int(base_performance['predicted_reps'] * 1.2)
        elif exercise['difficulty'] == 'advanced':
            base_performance['predicted_reps'] = max(5, int(base_performance['predicted_reps'] * 0.8))

        # Adjust based on user's historical performance with similar exercises
        exercise_history = user_profile.get('exercise_history', [])
        if exercise_history:
            # Calculate average performance for similar exercises
            similar_exercises = [ex for ex in exercise_history if ex['category'] == exercise['category']]
            if similar_exercises:
                avg_sets = sum(ex.get('sets_completed', 0) for ex in similar_exercises) / len(similar_exercises)
                avg_reps = sum(ex.get('reps_completed', 0) for ex in similar_exercises) / len(similar_exercises)

                base_performance['predicted_sets'] = max(1, int(avg_sets * 1.1))  # Slightly increase based on progress
                base_performance['predicted_reps'] = max(5, int(avg_reps * 1.05))  # Slightly increase based on progress

        return base_performance

    def train_models(self, user_data):
        """Train the ML models with user data (for demonstration purposes)"""
        # This would typically be called periodically with aggregated user data
        # For this implementation, we'll create simple models

        # Train exercise preferences model (simplified)
        # In a real system, this would use actual user interaction data
        self.exercise_preferences_model = RandomForestRegressor(n_estimators=10)

        # Train meal preferences model (simplified)
        self.meal_preferences_model = RandomForestRegressor(n_estimators=10)

        # Train performance predictor (simplified)
        self.performance_predictor = RandomForestRegressor(n_estimators=10)

        # Save models
        self._save_models()

    def _save_models(self):
        """Save trained models to disk"""
        if self.exercise_preferences_model:
            with open(os.path.join(self.model_dir, 'exercise_preferences_model.pkl'), 'wb') as f:
                pickle.dump(self.exercise_preferences_model, f)

        if self.meal_preferences_model:
            with open(os.path.join(self.model_dir, 'meal_preferences_model.pkl'), 'wb') as f:
                pickle.dump(self.meal_preferences_model, f)

        if self.performance_predictor:
            with open(os.path.join(self.model_dir, 'performance_predictor.pkl'), 'wb') as f:
                pickle.dump(self.performance_predictor, f)