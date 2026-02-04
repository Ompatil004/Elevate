"""
Meal Planning System with Dietary Constraints
Integrates rule-based logic and ML personalization for safe and nutritious meal plans
"""

from rules.nutrition_rules import NutritionRules
from ml.adaptive_engine import AdaptiveEngine
import random
from datetime import datetime, timedelta


class MealPlanGenerator:
    def __init__(self):
        self.nutrition_rules = NutritionRules()
        self.adaptive_engine = AdaptiveEngine()
    
    def generate_meal_plan(self, user_profile, plan_duration_days=7):
        """
        Generate a comprehensive meal plan for the user
        """
        # Calculate nutrition goals
        nutrition_goals = self.nutrition_rules.calculate_nutrition_goals(user_profile)
        
        # Apply rule-based filtering to get safe meals
        filtered_meals = self.nutrition_rules.filter_meals_by_rules(user_profile)
        
        # Apply ML-based personalization
        personalized_meals = self.adaptive_engine.personalize_meals(
            filtered_meals, 
            user_profile
        )
        
        # Generate daily meal plans
        daily_plans = []
        for day in range(plan_duration_days):
            daily_plan = self._create_daily_meal_plan(
                personalized_meals, 
                user_profile, 
                nutrition_goals,
                day
            )
            daily_plans.append(daily_plan)
        
        # Create weekly plan
        weekly_plan = {
            'user_id': user_profile.get('user_id'),
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=plan_duration_days-1)).strftime('%Y-%m-%d'),
            'daily_plans': daily_plans,
            'nutrition_goals': nutrition_goals,
            'summary': self._generate_summary(daily_plans, nutrition_goals),
            'rules_applied': self.nutrition_rules.get_applied_rules(),
            'ml_adjustments': self.adaptive_engine.get_adjustments()
        }
        
        return weekly_plan
    
    def _create_daily_meal_plan(self, personalized_meals, user_profile, nutrition_goals, day_offset):
        """
        Create a single day's meal plan
        """
        # Sort meals by preference score
        sorted_meals = sorted(
            personalized_meals, 
            key=lambda x: x.get('preference_score', 0), 
            reverse=True
        )
        
        # Determine meal distribution based on user's eating habits
        meal_distribution = self._determine_meal_distribution(user_profile)
        
        # Select meals for each category
        daily_plan = {
            'day': day_offset + 1,
            'date': (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d'),
            'meals': {},
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fats': 0,
            'nutrition_adherence': 0.0
        }
        
        selected_meals = set()  # Track selected meals to avoid repetition
        
        # Assign meals to each category
        for meal_type, count in meal_distribution.items():
            available_meals = [
                meal for meal in sorted_meals 
                if meal['category'] == meal_type and meal['name'] not in selected_meals
            ]
            
            selected_meal_list = []
            for _ in range(min(count, len(available_meals))):
                if available_meals:
                    meal = available_meals.pop(0)
                    selected_meals.add(meal['name'])
                    selected_meal_list.append(meal)
            
            daily_plan['meals'][meal_type] = selected_meal_list
        
        # Calculate daily totals
        self._calculate_daily_totals(daily_plan)
        
        # Assess nutrition adherence
        daily_plan['nutrition_adherence'] = self._assess_nutrition_adherence(
            daily_plan, nutrition_goals
        )
        
        return daily_plan
    
    def _determine_meal_distribution(self, user_profile):
        """
        Determine how many meals of each type based on user profile
        """
        # Default meal distribution
        distribution = {
            'breakfast': 1,
            'lunch': 1,
            'dinner': 1,
            'snack': 2  # Usually 2 snacks
        }
        
        # Adjust based on user preferences
        eating_frequency = user_profile.get('eating_frequency', 'regular')
        
        if eating_frequency == 'frequent_small_meals':
            distribution['snack'] = 3
        elif eating_frequency == 'three_large_meals':
            distribution['snack'] = 0
        
        # Adjust for specific dietary approaches
        if user_profile.get('goal') == 'intermittent_fasting':
            distribution['breakfast'] = 0  # Skip breakfast
            distribution['snack'] = 1  # Fewer snacks
        
        return distribution
    
    def _calculate_daily_totals(self, daily_plan):
        """
        Calculate total nutrition for the day
        """
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        
        for meal_type, meals in daily_plan['meals'].items():
            for meal in meals:
                total_calories += meal.get('calories', 0)
                total_protein += meal.get('protein_g', 0)
                total_carbs += meal.get('carbs_g', 0)
                total_fats += meal.get('fats_g', 0)
        
        daily_plan['total_calories'] = total_calories
        daily_plan['total_protein'] = total_protein
        daily_plan['total_carbs'] = total_carbs
        daily_plan['total_fats'] = total_fats
    
    def _assess_nutrition_adherence(self, daily_plan, nutrition_goals):
        """
        Assess how well the daily plan meets nutrition goals
        """
        # Calculate adherence percentages
        calorie_adherence = min(1.0, daily_plan['total_calories'] / nutrition_goals['daily_calories'])
        protein_adherence = min(1.0, daily_plan['total_protein'] / nutrition_goals['protein_g'])
        
        # Simple average for overall adherence
        adherence = (calorie_adherence + protein_adherence) / 2
        
        return adherence
    
    def _generate_summary(self, daily_plans, nutrition_goals):
        """
        Generate summary statistics for the plan
        """
        total_calories = sum(day['total_calories'] for day in daily_plans)
        avg_calories = total_calories / len(daily_plans) if daily_plans else 0
        
        total_protein = sum(day['total_protein'] for day in daily_plans)
        avg_protein = total_protein / len(daily_plans) if daily_plans else 0
        
        total_carbs = sum(day['total_carbs'] for day in daily_plans)
        avg_carbs = total_carbs / len(daily_plans) if daily_plans else 0
        
        total_fats = sum(day['total_fats'] for day in daily_plans)
        avg_fats = total_fats / len(daily_plans) if daily_plans else 0
        
        # Calculate adherence rate
        adherence_rate = sum(day['nutrition_adherence'] for day in daily_plans) / len(daily_plans) if daily_plans else 0
        
        # Count variety
        unique_meals = set()
        for day in daily_plans:
            for meal_type, meals in day['meals'].items():
                for meal in meals:
                    unique_meals.add(meal['name'])
        
        summary = {
            'total_days': len(daily_plans),
            'average_calories': round(avg_calories),
            'average_protein_g': round(avg_protein),
            'average_carbs_g': round(avg_carbs),
            'average_fats_g': round(avg_fats),
            'nutrition_goals_met_percentage': round(adherence_rate * 100, 1),
            'unique_meals_count': len(unique_meals),
            'meal_variety_score': min(10, round(len(unique_meals) / len(daily_plans) * 2, 1)),
            'primary_diet_type': self._determine_primary_diet_type(daily_plans),
            'safety_compliance': True,
            'personalization_level': 'high'
        }
        
        return summary
    
    def _determine_primary_diet_type(self, daily_plans):
        """
        Determine the primary diet type based on the meals
        """
        vegan_meals = 0
        vegetarian_meals = 0
        total_meals = 0
        
        for day in daily_plans:
            for meal_type, meals in day['meals'].items():
                for meal in meals:
                    total_meals += 1
                    if 'vegan' in meal.get('diet_types', []):
                        vegan_meals += 1
                    elif 'vegetarian' in meal.get('diet_types', []):
                        vegetarian_meals += 1
        
        if total_meals == 0:
            return 'balanced'
        
        vegan_ratio = vegan_meals / total_meals
        vegetarian_ratio = vegetarian_meals / total_meals
        
        if vegan_ratio > 0.8:
            return 'vegan'
        elif vegetarian_ratio > 0.8:
            return 'vegetarian'
        elif vegan_ratio > 0.5:
            return 'mostly_vegan'
        elif vegetarian_ratio > 0.5:
            return 'mostly_vegetarian'
        else:
            return 'balanced'
    
    def adjust_meal_plan(self, meal_plan, user_feedback):
        """
        Adjust meal plan based on user feedback
        """
        # Process feedback to improve future recommendations
        for feedback in user_feedback:
            meal_name = feedback.get('meal_name')
            rating = feedback.get('rating')  # 1-10 scale
            reason = feedback.get('reason', '')
            
            # Update internal models based on feedback
            # In a real system, this would update ML models
            pass
        
        # Return adjusted plan (for now, just return original)
        return meal_plan


# Example usage
if __name__ == "__main__":
    generator = MealPlanGenerator()
    
    # Sample user profile
    sample_user = {
        'user_id': 1,
        'weight': 70,  # kg
        'height': 170,  # cm
        'age': 30,
        'gender': 'male',
        'activity_level': 'moderate',
        'goal': 'muscle_gain',
        'dietary_restrictions': ['dairy_free'],
        'allergies': ['nuts'],
        'health_conditions': [],
        'preferred_cuisines': ['mediterranean', 'asian'],
        'disliked_ingredients': ['mushrooms', 'parsley'],
        'eating_frequency': 'regular',
        'meal_history': [
            {'meal': 'Grilled Chicken Salad', 'rating': 8},
            {'meal': 'Oatmeal with Berries', 'rating': 7}
        ],
        'dietary_preferences': {
            'high_protein': True,
            'low_carb': False,
            'high_fiber': True
        }
    }
    
    # Generate meal plan
    plan = generator.generate_meal_plan(sample_user)
    
    # Print plan summary
    print("Meal Plan Generated Successfully!")
    print(f"Duration: {plan['start_date']} to {plan['end_date']}")
    print(f"Days: {plan['summary']['total_days']}")
    print(f"Average Calories: {plan['summary']['average_calories']}")
    print(f"Average Protein: {plan['summary']['average_protein_g']}g")
    print(f"Nutrition Goals Met: {plan['summary']['nutrition_goals_met_percentage']}%")
    print(f"Diet Type: {plan['summary']['primary_diet_type']}")
    
    # Print first day's meals
    if plan['daily_plans']:
        first_day = plan['daily_plans'][0]
        print(f"\nFirst Day Meals:")
        for meal_type, meals in first_day['meals'].items():
            if meals:  # Only show meal types that have meals
                print(f"  {meal_type.title()}:")
                for meal in meals:
                    print(f"    - {meal['name']} ({meal['calories']} cal)")