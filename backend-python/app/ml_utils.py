import pandas as pd
import os
import random

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MLService:
    def __init__(self):
        # 1. Define Paths (Priority: Processed > Raw)
        self.ex_processed = os.path.join(BASE_DIR, 'data', 'exercises_processed.csv')
        self.ex_raw = os.path.join(BASE_DIR, 'data', 'exercises.csv')
        
        self.nut_processed = os.path.join(BASE_DIR, 'data', 'nutrition_processed.csv')
        self.nut_raw = os.path.join(BASE_DIR, 'data', 'nutrition.csv')

        self.df_ex = pd.DataFrame()
        self.df_nut = pd.DataFrame()
        
        self.load_data()

    def load_data(self):
        # --- LOAD EXERCISES ---
        if os.path.exists(self.ex_processed):
            self.df_ex = pd.read_csv(self.ex_processed)
            self.df_ex.rename(columns={'equipment': 'Equipment', 'name': 'Name'}, inplace=True)
        elif os.path.exists(self.ex_raw):
            self.df_ex = pd.read_csv(self.ex_raw)
        
        # --- LOAD NUTRITION ---
        if os.path.exists(self.nut_processed):
            self.df_nut = pd.read_csv(self.nut_processed)
            self.df_nut.rename(columns={'carbohydrate': 'Carbs', 'total_fat': 'Fats', 'name': 'Name'}, inplace=True)
        elif os.path.exists(self.nut_raw):
            self.df_nut = pd.read_csv(self.nut_raw)

        # Safety Fills to prevent crashes
        if not self.df_ex.empty:
            self.df_ex.fillna({'Avoid_If': 'None', 'Check_Type': 'general_logic', 'Progression_Next': ''}, inplace=True)
        if not self.df_nut.empty:
            self.df_nut.fillna({'Allergens': 'None', 'Swap_Group': 'Generic'}, inplace=True)

        print(f"Brain Loaded: {len(self.df_ex)} exercises, {len(self.df_nut)} meals ready.")

    def calculate_macros(self, user):
        """ Calculates BMR & Macros based on Goal """
        weight = user.get('weight', 70)
        height = user.get('height', 170)
        age = user.get('age', 25)
        
        if user.get('gender') == 'Male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        multipliers = {'Sedentary': 1.2, 'Lightly Active': 1.375, 'Moderately Active': 1.55, 'Very Active': 1.725}
        tdee = bmr * multipliers.get(user.get('activity_level', 'Sedentary'), 1.2)

        goal = user.get('goal', 'Maintenance')
        if 'Gain' in goal: target = tdee + 300
        elif 'Loss' in goal: target = tdee - 500
        else: target = tdee

        return {
            'calories': int(target),
            'protein': int((target * 0.3) / 4),
            'carbs': int((target * 0.4) / 4),
            'fats': int((target * 0.3) / 9)
        }

    def recommend_workout(self, user_profile, equipment_list):
        """ Generates the Fixed Plan (Objective #1) """
        # 1. Equipment Filter
        user_equip = [str(e).title() for e in equipment_list]
        if 'Bodyweight' not in user_equip: user_equip.append('Body Weight')
        
        pool = self.df_ex[self.df_ex['Equipment'].str.title().isin(user_equip)].copy()

        # 2. Injury Filter (Objective #1 - Safety)
        issues = user_profile.get('body_issues', [])
        for issue in issues:
            pool = pool[~pool['Avoid_If'].str.contains(issue, case=False, na=False)]

        # 3. Split Logic
        days = user_profile.get('days_per_week', 3)
        if days == 3: schedule = ['Full Body', 'Rest', 'Full Body', 'Rest', 'Full Body', 'Rest', 'Rest']
        elif days == 4: schedule = ['Upper', 'Lower', 'Rest', 'Upper', 'Lower', 'Rest', 'Rest']
        else: schedule = ['Push', 'Pull', 'Legs', 'Push', 'Pull', 'Rest', 'Rest']

        plan = []
        streak = user_profile.get('streak', 0)

        for day in schedule:
            if day == 'Rest':
                plan.append({'day': day, 'exercises': []})
                continue
            
            # Muscle Mapping
            if day == 'Full Body': targets = ['Chest', 'Back', 'Legs', 'Waist']
            elif day in ['Upper', 'Push']: targets = ['Chest', 'Shoulders', 'Triceps']
            elif day == 'Pull': targets = ['Back', 'Biceps']
            elif day in ['Lower', 'Legs']: targets = ['Legs', 'Waist']
            else: targets = ['Chest']

            daily_exercises = []
            for muscle in targets:
                candidates = pool[pool['Target_Muscle'].str.contains(muscle, case=False, na=False)]
                if not candidates.empty:
                    ex = candidates.sample(1).iloc[0]
                    
                    # --- OBJECTIVE #17: PROGRESSIVE OVERLOAD ---
                    final_name = ex['Name']
                    if streak > 30 and ex.get('Progression_Next') and isinstance(ex['Progression_Next'], str):
                         if len(ex['Progression_Next']) > 2: 
                             final_name = ex['Progression_Next']

                    daily_exercises.append({
                        'name': final_name,
                        'sets': 3,
                        'reps': "12-15",
                        'video': ex['Video_URL'],
                        'check_type': ex['Check_Type'],
                        'swap_option': ex['Alternative_Swap']
                    })
            
            plan.append({'day': day, 'exercises': daily_exercises})
            
        return plan

    def recommend_meals(self, goal, preference, allergies, target_calories):
        """ Generates Meal Plan (Objective #2) """
        pool = self.df_nut.copy()

        if preference == 'Veg': pool = pool[pool['Tags'].isin(['Veg', 'Vegan'])]
        elif preference == 'Vegan': pool = pool[pool['Tags'] == 'Vegan']

        for allergy in allergies:
            pool = pool[~pool['Allergens'].str.contains(allergy, case=False, na=False)]

        plan = {}
        targets = {'Breakfast': 0.25, 'Lunch': 0.35, 'Snack': 0.10, 'Dinner': 0.30}

        for meal_type, ratio in targets.items():
            cal_goal = target_calories * ratio
            candidates = pool[pool['Type'].str.contains(meal_type, case=False, na=False)]

            if not candidates.empty:
                candidates['diff'] = (candidates['calories'] - cal_goal).abs()
                best = candidates.sort_values('diff').iloc[0]

                plan[meal_type.lower()] = {
                    'name': best['Name'],
                    'calories': int(best['calories']),
                    'protein': float(best['protein']),
                    'swap_group': best['Swap_Group']
                }
        return plan

    def recommend_weekly_meals(self, goal, preference, allergies, weekly_workout_plan):
        """ Generates a fixed weekly meal plan aligned with the workout structure """
        pool = self.df_nut.copy()

        if preference == 'Veg': pool = pool[pool['Tags'].isin(['Veg', 'Vegan'])]
        elif preference == 'Vegan': pool = pool[pool['Tags'] == 'Vegan']

        for allergy in allergies:
            pool = pool[~pool['Allergens'].str.contains(allergy, case=False, na=False)]

        weekly_meal_plan = []

        # Generate a meal plan for each day of the week
        for day_idx in range(7):
            day_meal_plan = {
                'day_of_week': day_idx,
                'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_idx],
                'meals': {}
            }

            # Calculate daily calories based on workout intensity
            # For now, use a consistent daily calorie target
            daily_calories = 2000  # This would normally be calculated based on workout intensity

            # Define meal targets for each day
            targets = {'Breakfast': 0.25, 'Lunch': 0.35, 'Snack': 0.10, 'Dinner': 0.30}

            for meal_type, ratio in targets.items():
                cal_goal = daily_calories * ratio
                candidates = pool[pool['Type'].str.contains(meal_type, case=False, na=False)]

                if not candidates.empty:
                    candidates['diff'] = (candidates['calories'] - cal_goal).abs()
                    best = candidates.sort_values('diff').iloc[0]

                    day_meal_plan['meals'][meal_type.lower()] = {
                        'name': best['Name'],
                        'calories': int(best['calories']),
                        'protein': float(best['protein']),
                        'swap_group': best['Swap_Group']
                    }
                else:
                    # Default meal if none found
                    day_meal_plan['meals'][meal_type.lower()] = {
                        'name': f'Default {meal_type}',
                        'calories': int(cal_goal),
                        'protein': 15,
                        'swap_group': 'Generic'
                    }

            weekly_meal_plan.append(day_meal_plan)

        return weekly_meal_plan

    def recommend_weekly_workout(self, user_profile, equipment_list):
        """ Generates a 7-day weekly workout plan that repeats by default """
        # 1. Equipment Filter
        user_equip = [str(e).title() for e in equipment_list]
        if 'Bodyweight' not in user_equip: user_equip.append('Body Weight')

        pool = self.df_ex[self.df_ex['Equipment'].str.title().isin(user_equip)].copy()

        # 2. Injury Filter (Safety)
        issues = user_profile.get('body_issues', [])
        for issue in issues:
            pool = pool[~pool['Avoid_If'].str.contains(issue, case=False, na=False)]

        # 3. Weekly Split based on experience and days per week
        experience = user_profile.get('experience', 'Beginner')
        days = user_profile.get('days_per_week', 3)

        # Define weekly schedule based on experience and days
        if experience == 'Beginner':
            if days <= 3:
                schedule = ['Full Body', 'Rest', 'Full Body', 'Rest', 'Full Body', 'Rest', 'Rest']
            else:
                schedule = ['Full Body', 'Rest', 'Full Body', 'Rest', 'Full Body', 'Rest', 'Cardio']
        elif experience == 'Intermediate':
            if days <= 3:
                schedule = ['Push', 'Pull', 'Legs', 'Rest', 'Push', 'Rest', 'Rest']
            elif days <= 4:
                schedule = ['Upper', 'Lower', 'Rest', 'Upper', 'Lower', 'Rest', 'Rest']
            else:
                schedule = ['Push', 'Pull', 'Legs', 'Rest', 'Push', 'Pull', 'Rest']
        else:  # Advanced
            if days <= 3:
                schedule = ['Upper', 'Lower', 'Full Body', 'Rest', 'Upper', 'Rest', 'Rest']
            elif days <= 4:
                schedule = ['Push', 'Pull', 'Legs', 'Rest', 'Upper/Lower', 'Rest', 'Rest']
            else:
                schedule = ['Chest/Tris', 'Back/Bis', 'Legs', 'Shoulders', 'Arms/Cardio', 'Rest', 'Active Recovery']

        weekly_plan = []

        for day_idx, day in enumerate(schedule):
            day_plan = {'day': day, 'day_of_week': day_idx, 'exercises': []}

            if day == 'Rest':
                # Add light stretching or recovery activities
                day_plan['exercises'] = []
                day_plan['note'] = 'Rest Day'
            elif day == 'Cardio':
                # Add cardio exercises
                cardio_pool = pool[pool['Target_Muscle'].str.contains('cardio|cardiovascular|hiit', case=False, na=False)]
                if not cardio_pool.empty:
                    cardio_ex = cardio_pool.sample(1).iloc[0]
                    day_plan['exercises'] = [{
                        'name': cardio_ex['Name'],
                        'sets': 3,
                        'reps': "20-30 min",
                        'duration': "20-30 min",
                        'video': cardio_ex.get('Video_URL', ''),
                        'check_type': cardio_ex.get('Check_Type', 'cardio'),
                        'swap_option': cardio_ex.get('Alternative_Swap', '')
                    }]
                else:
                    # Default cardio if none found
                    day_plan['exercises'] = [{
                        'name': 'Brisk Walking/Jogging',
                        'sets': 1,
                        'reps': "20-30 min",
                        'duration': "20-30 min",
                        'video': '',
                        'check_type': 'cardio',
                        'swap_option': ''
                    }]
            elif day == 'Active Recovery':
                # Add light movement and stretching
                recovery_pool = pool[pool['Target_Muscle'].str.contains('stretch|flexibility|recovery', case=False, na=False)]
                if not recovery_pool.empty:
                    recovery_ex = recovery_pool.sample(min(2, len(recovery_pool))).to_dict('records')
                    day_plan['exercises'] = []
                    for ex in recovery_ex:
                        day_plan['exercises'].append({
                            'name': ex['Name'],
                            'sets': 2,
                            'reps': "10-15 reps",
                            'video': ex.get('Video_URL', ''),
                            'check_type': ex.get('Check_Type', 'recovery'),
                            'swap_option': ex.get('Alternative_Swap', '')
                        })
                else:
                    day_plan['exercises'] = [{
                        'name': 'Light Stretching',
                        'sets': 2,
                        'reps': "10-15 reps",
                        'duration': "15-20 min",
                        'video': '',
                        'check_type': 'recovery',
                        'swap_option': ''
                    }]
            else:
                # Muscle Mapping for workout days
                if day == 'Full Body': targets = ['Chest', 'Back', 'Legs', 'Shoulders', 'Waist']
                elif day in ['Upper', 'Chest/Tris', 'Push']: targets = ['Chest', 'Shoulders', 'Triceps']
                elif day in ['Lower', 'Legs']: targets = ['Legs', 'Glutes', 'Calves', 'Waist']
                elif day in ['Pull', 'Back/Bis']: targets = ['Back', 'Biceps', 'Forearms']
                elif day in ['Chest/Tris']: targets = ['Chest', 'Triceps', 'Shoulders']
                elif day in ['Back/Bis']: targets = ['Back', 'Biceps']
                elif day in ['Shoulders']: targets = ['Shoulders', 'Side Delts', 'Rear Delts']
                elif day in ['Arms/Cardio']: targets = ['Biceps', 'Triceps', 'Forearms']
                elif day in ['Upper/Lower']: targets = ['Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps']
                else: targets = ['Chest']  # fallback

                daily_exercises = []
                for muscle in targets:
                    candidates = pool[pool['Target_Muscle'].str.contains(muscle, case=False, na=False)]
                    if not candidates.empty:
                        ex = candidates.sample(1).iloc[0]

                        # Determine sets/reps based on experience
                        if experience == 'Beginner':
                            sets_reps = "2-3 sets of 8-12 reps"
                        elif experience == 'Intermediate':
                            sets_reps = "3-4 sets of 8-12 reps"
                        else:  # Advanced
                            sets_reps = "4-5 sets of 6-10 reps"

                        daily_exercises.append({
                            'name': ex['Name'],
                            'sets': int(sets_reps.split()[0]),
                            'reps': sets_reps.split('of ')[1],
                            'video': ex.get('Video_URL', ''),
                            'check_type': ex.get('Check_Type', 'strength'),
                            'swap_option': ex.get('Alternative_Swap', ''),
                            'primary_muscle': muscle
                        })

                day_plan['exercises'] = daily_exercises
                day_plan['note'] = f'{experience} {day} Workout'

            weekly_plan.append(day_plan)

        return weekly_plan

    # --- NEW: SWAP FUNCTION (Restored for your Button) ---
    def get_alternative_meal(self, swap_group, exclude_name):
        """ Finds a different meal in the same group """
        pool = self.df_nut[self.df_nut['Swap_Group'] == swap_group]
        pool = pool[pool['Name'] != exclude_name]

        if pool.empty:
            return None

        best = pool.sample(1).iloc[0]
        return {
            'name': best['Name'],
            'calories': int(best['calories']),
            'protein': float(best['protein']),
            'swap_group': best['Swap_Group']
        }

# Create Singleton
ml_service = MLService()