"""
Explainability Controller for explaining recommendations
"""

from flask import jsonify


class ExplainabilityController:
    def __init__(self):
        pass

    def explain_workout_recommendation(self, request_data):
        """Explain why certain exercises were recommended"""
        try:
            workout_plan = request_data.get('workout_plan', {})

            # Extract relevant information from the workout plan
            user_profile = request_data.get('user_profile', {})
            exercises = workout_plan.get('daily_plans', [{}])[0].get('exercises', []) if workout_plan.get('daily_plans') else workout_plan.get('exercises', [])

            explanation = {
                'rule_based_explanations': self._get_detailed_rule_explanations(user_profile, exercises),
                'ml_based_adjustments': workout_plan.get('ml_adjustments', []),
                'safety_considerations': self._get_safety_explanations(user_profile, exercises),
                'personalization_factors': self._get_personalization_explanations(user_profile, exercises),
                'training_principles_applied': self._get_training_principles_explanation(workout_plan),
                'progression_logic': self._get_progression_logic(user_profile)
            }

            return jsonify({
                'success': True,
                'explanation': explanation
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def explain_meal_recommendation(self, request_data):
        """Explain why certain meals were recommended"""
        try:
            meal_plan = request_data.get('meal_plan', {})
            user_profile = request_data.get('user_profile', {})

            # Extract daily meals if it's a weekly plan
            daily_meals = []
            if 'daily_plans' in meal_plan:
                for day_plan in meal_plan['daily_plans']:
                    for meal_type, meals in day_plan.get('meals', {}).items():
                        daily_meals.extend(meals)
            else:
                daily_meals = meal_plan.get('meals', [])

            explanation = {
                'rule_based_explanations': self._get_detailed_nutrition_explanations(user_profile, daily_meals),
                'ml_based_adjustments': meal_plan.get('ml_adjustments', []),
                'nutritional_considerations': self._get_detailed_nutritional_explanations(user_profile, meal_plan),
                'dietary_restrictions_followed': self._get_dietary_restriction_explanations(user_profile, daily_meals),
                'health_condition_accommodations': self._get_health_condition_explanations(user_profile),
                'personalization_factors': self._get_meal_personalization_explanations(user_profile, daily_meals)
            }

            return jsonify({
                'success': True,
                'explanation': explanation
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def _get_detailed_rule_explanations(self, user_profile, exercises):
        """Get detailed rule-based explanations for exercises"""
        explanations = []

        # Injury-based exclusions
        injuries = user_profile.get('injuries', [])
        if injuries:
            explanations.append(f"Applied injury-based exclusions for: {', '.join(injuries)}")

        # Equipment availability
        equipment = user_profile.get('equipment_available', [])
        if equipment:
            explanations.append(f"Selected exercises matching available equipment: {', '.join(equipment)}")

        # Fitness level considerations
        fitness_level = user_profile.get('fitness_level', 'intermediate')
        explanations.append(f"Adjusted exercise selection for {fitness_level} fitness level")

        # Age-based modifications
        age = user_profile.get('age', 30)
        if age > 65:
            explanations.append("Limited high-impact exercises due to age considerations")
        elif age < 18:
            explanations.append("Focused on form over heavy loads due to age")

        # Health condition considerations
        health_conditions = user_profile.get('health_conditions', [])
        if health_conditions:
            explanations.append(f"Incorporated modifications for health conditions: {', '.join(health_conditions)}")

        return explanations

    def _get_safety_explanations(self, user_profile, exercises):
        """Get safety-related explanations for workout plan"""
        explanations = []

        # Intensity appropriate for level
        fitness_level = user_profile.get('fitness_level', 'intermediate')
        explanations.append(f"Intensity set appropriately for {fitness_level} fitness level")

        # Volume limits
        if fitness_level == 'beginner':
            explanations.append("Volume limited to prevent overtraining for beginner level")
        elif fitness_level == 'advanced':
            explanations.append("Higher volume prescribed for advanced adaptation")

        # Exercise sequencing
        explanations.append("Exercises sequenced to prevent injury and maximize effectiveness")

        # Rest period inclusion
        explanations.append("Appropriate rest periods included based on exercise intensity")

        return explanations

    def _get_personalization_explanations(self, user_profile, exercises):
        """Get personalization-related explanations for workout plan"""
        explanations = []

        # Preference-based selections
        preferred_categories = user_profile.get('preferred_categories', [])
        if preferred_categories:
            explanations.append(f"Prioritized exercises in preferred categories: {', '.join(preferred_categories)}")

        # Goal alignment
        goal = user_profile.get('goal', 'general_fitness')
        explanations.append(f"Exercises selected to align with '{goal}' goal")

        # Historical performance
        exercise_history = user_profile.get('exercise_history', [])
        if exercise_history:
            explanations.append("Considered historical performance and preferences")

        # Time availability
        time_available = user_profile.get('time_available', 45)
        explanations.append(f"Workout duration tailored to {time_available} minutes available time")

        return explanations

    def _get_training_principles_explanation(self, workout_plan):
        """Explain the training principles applied"""
        explanations = []

        # Progressive overload
        explanations.append("Applied progressive overload principle for continued adaptation")

        # Specificity
        explanations.append("Exercises selected based on specificity principle for goal-oriented training")

        # Recovery
        explanations.append("Adequate recovery time scheduled between sessions")

        # Variation
        explanations.append("Implemented variation to prevent plateaus and maintain engagement")

        return explanations

    def _get_progression_logic(self, user_profile):
        """Explain the progression logic used"""
        explanations = []

        # Based on performance data
        performance_data = user_profile.get('performance_data', {})
        if performance_data:
            explanations.append("Progression based on individual performance history")

        # Gradual increases
        explanations.append("Following 5-10% weekly volume/inensity increases")

        # Deload scheduling
        explanations.append("Periodic deload weeks scheduled to prevent overtraining")

        return explanations

    def _get_detailed_nutrition_explanations(self, user_profile, meals):
        """Get detailed rule-based explanations for meals"""
        explanations = []

        # Caloric target
        goals = self._calculate_user_goals(user_profile)
        explanations.append(f"Caloric target set to {goals['daily_calories']} for {user_profile.get('goal', 'general')} goal")

        # Macronutrient distribution
        macro_ratios = self._get_macro_ratios(user_profile.get('goal', 'maintenance'))
        explanations.append(f"Macronutrient distribution: {macro_ratios}")

        # Meal timing
        explanations.append("Meals distributed throughout the day for optimal nutrient timing")

        # Nutrient density
        explanations.append("Prioritized nutrient-dense foods for optimal vitamin and mineral intake")

        return explanations

    def _get_dietary_restriction_explanations(self, user_profile, meals):
        """Explain how dietary restrictions were followed"""
        explanations = []

        # Dietary restrictions
        restrictions = user_profile.get('dietary_restrictions', [])
        if restrictions:
            explanations.append(f"Dietary restrictions followed: {', '.join(restrictions)}")

        # Allergy considerations
        allergies = user_profile.get('allergies', [])
        if allergies:
            explanations.append(f"Allergen-free meals selected: {', '.join(allergies)}")

        # Health condition accommodations
        health_conditions = user_profile.get('health_conditions', [])
        if 'diabetes' in health_conditions:
            explanations.append("Low glycemic index foods selected for blood sugar management")
        if 'hypertension' in health_conditions:
            explanations.append("Low sodium preparations used")

        return explanations

    def _get_health_condition_explanations(self, user_profile):
        """Explain accommodations for health conditions"""
        explanations = []

        health_conditions = user_profile.get('health_conditions', [])
        if 'cardiac_issues' in health_conditions:
            explanations.append("Heart-healthy cooking methods and ingredients used")
        if 'diabetes' in health_conditions:
            explanations.append("Carbohydrate counting and glycemic load considered")
        if 'kidney_issues' in health_conditions:
            explanations.append("Protein and sodium levels adjusted accordingly")

        return explanations

    def _get_meal_personalization_explanations(self, user_profile, meals):
        """Get personalization explanations for meal plan"""
        explanations = []

        # Cuisine preferences
        cuisines = user_profile.get('preferred_cuisines', [])
        if cuisines:
            explanations.append(f"Cuisine preferences incorporated: {', '.join(cuisines)}")

        # Taste preferences
        taste_prefs = user_profile.get('taste_preferences', {})
        if taste_prefs:
            explanations.append(f"Taste preferences considered: {', '.join(taste_prefs.keys())}")

        # Cultural preferences
        cultural_prefs = user_profile.get('cultural_preferences', {})
        if cultural_prefs:
            explanations.append("Cultural food preferences respected")

        # Meal history
        meal_history = user_profile.get('meal_history', [])
        if meal_history:
            explanations.append("Previous meal ratings and preferences considered")

        return explanations

    def _calculate_user_goals(self, user_profile):
        """Helper to calculate user nutrition goals"""
        weight = user_profile.get('weight', 70)  # kg
        height = user_profile.get('height', 170)  # cm
        age = user_profile.get('age', 30)
        gender = user_profile.get('gender', 'male')
        activity_level = user_profile.get('activity_level', 'moderate')
        goal = user_profile.get('goal', 'maintenance')

        # Calculate BMR (Basal Metabolic Rate)
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # Adjust for activity level
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)

        # Adjust for goal
        goal_adjustments = {
            'weight_loss': tdee - 500,  # 500 calorie deficit
            'muscle_gain': tdee + 300,  # 300 calorie surplus
            'maintenance': tdee,
            'endurance': tdee * 1.1  # 10% extra for endurance
        }
        daily_calories = goal_adjustments.get(goal, tdee)

        return {'daily_calories': round(daily_calories)}

    def _get_macro_ratios(self, goal):
        """Get macronutrient ratios based on goal"""
        ratios = {
            'weight_loss': {'protein': '30%', 'carbs': '40%', 'fats': '30%'},
            'muscle_gain': {'protein': '35%', 'carbs': '45%', 'fats': '20%'},
            'maintenance': {'protein': '25%', 'carbs': '50%', 'fats': '25%'},
            'endurance': {'protein': '15%', 'carbs': '60%', 'fats': '25%'}
        }
        return ratios.get(goal, ratios['maintenance'])