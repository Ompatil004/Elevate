"""
Nutrition Rules module for rule-based meal selection and dietary constraints
"""

class NutritionRules:
    def __init__(self):
        # Define macronutrient ratios by goal
        self.macro_ratios = {
            'weight_loss': {'protein': 0.30, 'carbs': 0.40, 'fats': 0.30},
            'muscle_gain': {'protein': 0.35, 'carbs': 0.45, 'fats': 0.20},
            'maintenance': {'protein': 0.25, 'carbs': 0.50, 'fats': 0.25},
            'endurance': {'protein': 0.15, 'carbs': 0.60, 'fats': 0.25}
        }
        
        # Define dietary restrictions
        self.dietary_restrictions = {
            'vegan': ['meat', 'fish', 'dairy', 'eggs', 'honey'],
            'vegetarian': ['meat', 'fish'],
            'gluten_free': ['wheat', 'barley', 'rye', 'oats_unspecified'],
            'dairy_free': ['milk', 'cheese', 'yogurt', 'butter'],
            'keto': ['sugar', 'grains', 'most_fruits', 'starchy_vegetables']
        }
        
        # Define allergens
        self.allergens = [
            'nuts', 'peanuts', 'shellfish', 'eggs', 
            'soy', 'wheat', 'fish', 'milk'
        ]

    def filter_meals_by_rules(self, user_profile):
        """Apply rule-based filtering to meals based on user profile"""
        # Start with all meals
        all_meals = self._get_all_meals()
        
        # Apply dietary restrictions
        filtered_meals = self._apply_dietary_restrictions(all_meals, user_profile)
        
        # Apply allergen exclusions
        filtered_meals = self._apply_allergen_exclusions(filtered_meals, user_profile)
        
        # Apply health condition exclusions
        filtered_meals = self._apply_health_condition_exclusions(filtered_meals, user_profile)
        
        return filtered_meals

    def calculate_nutrition_goals(self, user_profile):
        """Calculate nutrition goals based on user profile"""
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
        
        # Calculate macro targets based on goal
        macro_targets = self.macro_ratios.get(goal, self.macro_ratios['maintenance'])
        
        return {
            'daily_calories': round(daily_calories),
            'protein_g': round((daily_calories * macro_targets['protein']) / 4),
            'carbs_g': round((daily_calories * macro_targets['carbs']) / 4),
            'fats_g': round((daily_calories * macro_targets['fats']) / 9)
        }

    def get_applied_rules(self):
        """Return list of rules applied during filtering"""
        return [
            "Dietary restriction filtering applied",
            "Allergen exclusions applied",
            "Health condition considerations applied",
            "Nutritional goal calculations applied"
        ]

    def _get_all_meals(self):
        """Get all available meals"""
        return [
            {
                'name': 'Grilled Chicken Salad',
                'category': 'lunch',
                'calories': 450,
                'protein_g': 35,
                'carbs_g': 15,
                'fats_g': 25,
                'ingredients': ['chicken', 'lettuce', 'tomatoes', 'olive_oil', 'cheese'],
                'diet_types': ['non_vegetarian', 'gluten_free']
            },
            {
                'name': 'Vegan Buddha Bowl',
                'category': 'lunch',
                'calories': 400,
                'protein_g': 15,
                'carbs_g': 50,
                'fats_g': 15,
                'ingredients': ['quinoa', 'kale', 'sweet_potato', 'avocado', 'tahini'],
                'diet_types': ['vegan', 'gluten_free']
            },
            {
                'name': 'Oatmeal with Berries',
                'category': 'breakfast',
                'calories': 350,
                'protein_g': 10,
                'carbs_g': 60,
                'fats_g': 8,
                'ingredients': ['oats', 'berries', 'almond_milk', 'nuts'],
                'diet_types': ['vegetarian', 'dairy_free']
            },
            {
                'name': 'Protein Shake',
                'category': 'snack',
                'calories': 200,
                'protein_g': 25,
                'carbs_g': 15,
                'fats_g': 3,
                'ingredients': ['protein_powder', 'banana', 'almond_milk', 'spinach'],
                'diet_types': ['vegetarian', 'dairy_free']
            },
            {
                'name': 'Salmon with Vegetables',
                'category': 'dinner',
                'calories': 500,
                'protein_g': 35,
                'carbs_g': 20,
                'fats_g': 30,
                'ingredients': ['salmon', 'broccoli', 'asparagus', 'olive_oil'],
                'diet_types': ['non_vegetarian', 'gluten_free']
            },
            {
                'name': 'Lentil Curry with Rice',
                'category': 'dinner',
                'calories': 450,
                'protein_g': 18,
                'carbs_g': 65,
                'fats_g': 12,
                'ingredients': ['lentils', 'rice', 'coconut_milk', 'spices'],
                'diet_types': ['vegan', 'gluten_free']
            },
            {
                'name': 'Greek Yogurt with Granola',
                'category': 'breakfast',
                'calories': 300,
                'protein_g': 15,
                'carbs_g': 35,
                'fats_g': 10,
                'ingredients': ['greek_yogurt', 'granola', 'honey', 'berries'],
                'diet_types': ['vegetarian']
            },
            {
                'name': 'Tofu Stir Fry',
                'category': 'dinner',
                'calories': 400,
                'protein_g': 20,
                'carbs_g': 45,
                'fats_g': 15,
                'ingredients': ['tofu', 'mixed_vegetables', 'soy_sauce', 'sesame_oil', 'brown_rice'],
                'diet_types': ['vegan', 'gluten_free']
            }
        ]

    def _apply_dietary_restrictions(self, meals, user_profile):
        """Filter meals based on dietary restrictions"""
        dietary_restrictions = user_profile.get('dietary_restrictions', [])
        
        if not dietary_restrictions:
            return meals
            
        filtered_meals = []
        for meal in meals:
            include_meal = True
            
            # Check if meal contains restricted ingredients
            for restriction in dietary_restrictions:
                if restriction in self.dietary_restrictions:
                    restricted_ingredients = self.dietary_restrictions[restriction]
                    meal_ingredients = [ing.lower() for ing in meal['ingredients']]
                    
                    # If any restricted ingredient is in the meal, exclude it
                    if any(restr_ing.lower() in meal_ingredients for restr_ing in restricted_ingredients):
                        include_meal = False
                        break
            
            if include_meal:
                filtered_meals.append(meal)
        
        return filtered_meals

    def _apply_allergen_exclusions(self, meals, user_profile):
        """Filter meals based on user allergies"""
        allergies = user_profile.get('allergies', [])
        
        if not allergies:
            return meals
            
        filtered_meals = []
        for meal in meals:
            include_meal = True
            
            # Check if meal contains allergens
            meal_ingredients = [ing.lower() for ing in meal['ingredients']]
            for allergen in allergies:
                if allergen.lower() in meal_ingredients:
                    include_meal = False
                    break
            
            if include_meal:
                filtered_meals.append(meal)
        
        return filtered_meals

    def _apply_health_condition_exclusions(self, meals, user_profile):
        """Filter meals based on health conditions"""
        health_conditions = user_profile.get('health_conditions', [])
        
        # For diabetes, limit high-sugar meals
        if 'diabetes' in health_conditions:
            filtered_meals = []
            for meal in meals:
                # Simple check: exclude meals with high sugar ingredients
                high_sugar_ingredients = ['sugar', 'honey', 'syrup', 'jam', 'candy']
                meal_ingredients = [ing.lower() for ing in meal['ingredients']]
                
                if not any(sugar_ing in meal_ingredients for sugar_ing in high_sugar_ingredients):
                    filtered_meals.append(meal)
            meals = filtered_meals
        
        # For heart disease, limit high sodium and saturated fat
        if 'heart_disease' in health_conditions:
            # In a real system, we'd have more detailed nutritional info
            # For now, we'll just return all meals but note the consideration
            pass
        
        return meals