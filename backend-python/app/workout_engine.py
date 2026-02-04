import pandas as pd
import numpy as np
import os
from typing import List, Dict
import joblib

class WorkoutEngine:
    def __init__(self):
        print("\n🏋️ Initializing WorkoutEngine...")

        # Get base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exercises_processed = os.path.join(base_dir, 'data', 'exercises_processed.csv')
        exercises_raw = os.path.join(base_dir, 'data', 'exercises.csv')

        # Load exercises from CSV or create fallback
        try:
            if os.path.exists(exercises_processed):
                self.exercises_df = pd.read_csv(exercises_processed)
                print(f"✅ Loaded {len(self.exercises_df)} exercises from processed CSV")
                # Standardize column names to TitleCase format to match expected format
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')
            elif os.path.exists(exercises_raw):
                self.exercises_df = pd.read_csv(exercises_raw)
                print(f"✅ Loaded {len(self.exercises_df)} exercises from raw CSV")
                # Standardize column names to TitleCase format to match expected format
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')
            else:
                # Fallback exercises
                print("⚠️ CSV files not found, using fallback exercises")
                self.exercises_df = pd.DataFrame({
                    'Name': [
                        'Push-ups', 'Squats', 'Deadlifts', 'Bench Press',
                        'Dumbbell Rows', 'Pull-ups', 'Lunges', 'Plank',
                        'Bicep Curls', 'Tricep Dips', 'Shoulder Press', 'Leg Press',
                        'Lat Pulldown', 'Chest Fly', 'Leg Curl', 'Calf Raises'
                    ],
                    'Target_Muscle': [
                        'Chest', 'Legs', 'Back', 'Chest',
                        'Back', 'Back', 'Legs', 'Core',
                        'Arms', 'Arms', 'Shoulders', 'Legs',
                        'Back', 'Chest', 'Legs', 'Legs'
                    ],
                    'Equipment': [
                        'Body Weight', 'Body Weight', 'Barbell', 'Barbell',
                        'Dumbbell', 'Body Weight', 'Body Weight', 'Body Weight',
                        'Dumbbell', 'Body Weight', 'Dumbbell', 'Machine',
                        'Machine', 'Dumbbell', 'Machine', 'Body Weight'
                    ],
                    'Avoid_If': [
                        'None', 'Knee Issues', 'Back Issues', 'Shoulder Issues',
                        'None', 'Shoulder Issues', 'Knee Issues', 'None',
                        'None', 'Shoulder Issues', 'Shoulder Issues', 'Knee Issues',
                        'None', 'Shoulder Issues', 'None', 'None'
                    ],
                    'Check_Type': ['strength'] * 16,
                    'Risk_Level': ['Low', 'Medium', 'High', 'High', 'Medium', 'Medium', 'Medium', 'Low', 'Low', 'Low', 'Medium', 'Medium', 'Medium', 'Low', 'Low', 'Low'],
                    'Progression_Next': [''] * 16,
                    'Alternative_Swap': [''] * 16
                })

                # Standardize column names for fallback DataFrame too
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')

            # Fill missing values
            fill_values = {
                'Avoid_If': 'None',
                'Check_Type': 'strength',
                'Progression_Next': '',
                'Alternative_Swap': ''
            }

            for col, val in fill_values.items():
                if col in self.exercises_df.columns:
                    self.exercises_df[col].fillna(val, inplace=True)

        except Exception as e:
            print(f"❌ Error loading exercises: {e}")
            raise

        # Load ML models
        self.xgb_volume_model = None
        self.xgb_intensity_model = None
        self.xgb_split_model = None
        self.xgb_frequency_model = None
        self.xgb_sets_model = None
        self.xgb_reps_model = None
        self.xgb_rest_model = None
        self.xgb_progression_model = None
        self.le_goal = None
        self.le_experience = None
        self._load_ml_models()

        print(f"✅ WorkoutEngine initialized successfully!\n")

    def _load_ml_models(self):
        """Load pre-trained ML models (optional)"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'models')

            # Load multiple models for different aspects
            volume_path = os.path.join(model_dir, 'xgboost_volume.pkl')
            intensity_path = os.path.join(model_dir, 'xgboost_intensity.pkl')
            split_path = os.path.join(model_dir, 'xgboost_split.pkl')
            frequency_path = os.path.join(model_dir, 'xgboost_frequency.pkl')
            sets_path = os.path.join(model_dir, 'xgboost_sets.pkl')
            reps_path = os.path.join(model_dir, 'xgboost_reps.pkl')
            rest_path = os.path.join(model_dir, 'xgboost_rest.pkl')
            progression_path = os.path.join(model_dir, 'xgboost_progression.pkl')
            le_goal_path = os.path.join(model_dir, 'label_encoder_goal.pkl')
            le_exp_path = os.path.join(model_dir, 'label_encoder_experience.pkl')

            if os.path.exists(volume_path):
                self.xgb_volume_model = joblib.load(volume_path)
                print("✅ Volume ML model loaded successfully")
            else:
                print("⚠️ Volume ML model not found, using rule-based system")

            if os.path.exists(intensity_path):
                self.xgb_intensity_model = joblib.load(intensity_path)
                print("✅ Intensity ML model loaded successfully")
            else:
                print("⚠️ Intensity ML model not found, using rule-based system")

            if os.path.exists(split_path):
                self.xgb_split_model = joblib.load(split_path)
                print("✅ Split ML model loaded successfully")
            else:
                print("⚠️ Split ML model not found, using rule-based system")

            if os.path.exists(frequency_path):
                self.xgb_frequency_model = joblib.load(frequency_path)
                print("✅ Frequency ML model loaded successfully")
            else:
                print("⚠️ Frequency ML model not found, using rule-based system")

            if os.path.exists(sets_path):
                self.xgb_sets_model = joblib.load(sets_path)
                print("✅ Sets ML model loaded successfully")
            else:
                print("⚠️ Sets ML model not found, using rule-based system")

            if os.path.exists(reps_path):
                self.xgb_reps_model = joblib.load(reps_path)
                print("✅ Reps ML model loaded successfully")
            else:
                print("⚠️ Reps ML model not found, using rule-based system")

            if os.path.exists(rest_path):
                self.xgb_rest_model = joblib.load(rest_path)
                print("✅ Rest ML model loaded successfully")
            else:
                print("⚠️ Rest ML model not found, using rule-based system")

            if os.path.exists(progression_path):
                self.xgb_progression_model = joblib.load(progression_path)
                print("✅ Progression ML model loaded successfully")
            else:
                print("⚠️ Progression ML model not found, using rule-based system")

            if os.path.exists(le_goal_path):
                self.le_goal = joblib.load(le_goal_path)
                print("✅ Goal label encoder loaded successfully")
            else:
                print("⚠️ Goal label encoder not found")

            if os.path.exists(le_exp_path):
                self.le_experience = joblib.load(le_exp_path)
                print("✅ Experience label encoder loaded successfully")
            else:
                print("⚠️ Experience label encoder not found")

        except Exception as e:
            print(f"⚠️ Could not load ML models: {e}")
            self.xgb_volume_model = None
            self.xgb_intensity_model = None
            self.xgb_split_model = None
            self.xgb_frequency_model = None
            self.xgb_sets_model = None
            self.xgb_reps_model = None
            self.xgb_rest_model = None
            self.xgb_progression_model = None
            self.le_goal = None
            self.le_experience = None

    def filter_by_equipment(self, exercises: pd.DataFrame, available_equipment: List[str]) -> pd.DataFrame:
        """Filter exercises by available equipment - RULE-BASED SAFETY LOGIC"""
        if not available_equipment or exercises.empty:
            return exercises

        try:
            if 'Equipment' not in exercises.columns:
                print("⚠️ 'Equipment' column not found")
                return exercises

            equipment_lower = [str(e).lower().strip() for e in available_equipment]

            # Add variations
            if 'dumbbell' in equipment_lower:
                equipment_lower.append('dumbbells')
            if 'barbell' in equipment_lower:
                equipment_lower.append('barbells')

            # Always include bodyweight
            bodyweight_terms = ['body weight', 'bodyweight', 'none', 'no equipment']
            equipment_lower.extend(bodyweight_terms)

            filtered = exercises[
                exercises['Equipment'].str.lower().str.strip().isin(equipment_lower)
            ]

            if filtered.empty:
                print(f"⚠️ No exercises for equipment: {available_equipment}, returning all")
                return exercises

            print(f"✅ Filtered to {len(filtered)} exercises")
            return filtered

        except Exception as e:
            print(f"⚠️ Error filtering by equipment: {e}")
            return exercises

    def filter_by_injuries(self, exercises: pd.DataFrame, body_issues: List[str]) -> pd.DataFrame:
        """Filter exercises to avoid injuries - RULE-BASED SAFETY LOGIC"""
        if not body_issues or exercises.empty:
            return exercises

        try:
            if 'Avoid_If' not in exercises.columns:
                print("⚠️ 'Avoid_If' column not found")
                return exercises

            filtered = exercises.copy()

            for issue in body_issues:
                filtered = filtered[
                    ~filtered['Avoid_If'].str.contains(issue, case=False, na=False)
                ]

            if filtered.empty:
                print(f"⚠️ All exercises filtered out by injuries, returning safe defaults")
                return exercises

            print(f"✅ Filtered out exercises for: {body_issues}")
            return filtered

        except Exception as e:
            print(f"⚠️ Error filtering by injuries: {e}")
            return exercises

    def _build_feature_vector(self, profile: dict) -> np.ndarray:
        """Build a comprehensive feature vector for ML models"""
        # Encode categorical features
        goal_map = {'Weight Loss': 0, 'Muscle Gain': 1, 'Maintenance': 2, 'Athletic Performance': 3, 'Strength': 4, 'Endurance': 5}
        exp_map = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}

        goal_encoded = goal_map.get(profile.get('goal', 'Muscle Gain'), 1)
        experience_encoded = exp_map.get(profile.get('experience', 'Beginner'), 0)

        # Extract numerical features with defaults (safe casting)
        def _to_num(val, default):
            try:
                return float(val)
            except Exception:
                return default

        age = int(_to_num(profile.get('age', 30), 30))
        weight = _to_num(profile.get('weight', 70), 70)
        height = _to_num(profile.get('height', 175), 175)
        gender = profile.get('gender', 'Male')
        gender_encoded = 1 if str(gender).lower() == 'male' else 0

        streak = int(_to_num(profile.get('streak', 0), 0))
        consistency = _to_num(profile.get('consistency', 0.7), 0.7)
        days_per_week = int(_to_num(profile.get('days_per_week', 4), 4))

        # Calculate BMI (guard height)
        bmi = weight / ((height / 100) ** 2) if height and height > 0 else 22.5

        # Create feature vector
        features = np.array([
            age,
            weight,
            height,
            bmi,
            gender_encoded,
            goal_encoded,
            experience_encoded,
            streak,
            consistency,
            days_per_week,
            len(profile.get('equipment', [])) if isinstance(profile.get('equipment', []), list) else 0,
            len(profile.get('body_issues', [])) if isinstance(profile.get('body_issues', []), list) else 0
        ])

        return features

    def _get_intensity_adjustment(self, profile: dict) -> float:
        """Get intensity adjustment based on ML model or rules - HYBRID APPROACH"""
        feature_vector = self._build_feature_vector(profile)

        if self.xgb_intensity_model is not None:
            try:
                ml_intensity = self.xgb_intensity_model.predict(feature_vector.reshape(1, -1))[0]
                validated_intensity = max(0.5, min(1.0, ml_intensity))
                print(f"   🤖 ML predicted intensity: {ml_intensity:.2f}, validated: {validated_intensity:.2f}")
                return float(validated_intensity)
            except Exception as e:
                print(f"⚠️ ML intensity prediction failed: {e}")

        experience = profile.get('experience', 'Beginner')
        if experience == 'Beginner':
            return 0.7
        elif experience == 'Intermediate':
            return 0.85
        else:
            return 1.0

    def _get_optimized_workout_split(self, profile: dict, days_per_week: int) -> List[str]:
        """Get workout split optimized by ML model with rule-based validation - HYBRID APPROACH"""
        allowed_splits = {
            1: [['Full Body']],
            2: [['Upper Body', 'Lower Body'], ['Push', 'Pull']],
            3: [['Upper Body', 'Lower Body', 'Full Body'], ['Push', 'Pull', 'Legs']],
            4: [['Chest & Triceps', 'Back & Biceps', 'Legs', 'Shoulders & Core']],
            5: [['Chest', 'Back', 'Legs', 'Shoulders', 'Arms']],
            6: [['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core']],
            7: [['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Active Recovery']]
        }

        if self.xgb_split_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_split_model.predict(feature_vector.reshape(1, -1))[0]
                split_idx = int(ml_prediction) % len(allowed_splits.get(days_per_week, allowed_splits[4]))
                valid_splits = allowed_splits.get(days_per_week, allowed_splits[4])
                split = valid_splits[split_idx % len(valid_splits)]
                print(f"   🤖 ML selected split: {split}")
                return split
            except Exception as e:
                print(f"⚠️ ML split selection failed: {e}")

        return self._generate_dynamic_split(days_per_week, profile.get('goal', 'Muscle Gain'))

    def _get_optimized_training_volume(self, profile: dict) -> tuple:
        """Get optimized training volume (sets, reps, rest) using ML with rule-based validation - HYBRID APPROACH"""
        if self.xgb_volume_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_volume_model.predict(feature_vector.reshape(1, -1))[0]
                volume_level = int(ml_prediction) % 3
                base_sets = 3 + volume_level
                base_reps = ['8-12', '6-10', '4-8'][volume_level]
                base_rest = [60, 90, 120][volume_level]

                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    base_sets = min(base_sets, 4)
                    base_rest = max(base_rest, 60)

                if goal == 'Endurance':
                    base_reps = '12-15'
                    base_rest = 30

                print(f"   🤖 ML optimized volume: {base_sets} sets, {base_reps} reps, {base_rest}s rest")
                return base_sets, base_reps, base_rest
            except Exception as e:
                print(f"⚠️ ML volume optimization failed: {e}")

        experience = profile.get('experience', 'Beginner')
        goal = profile.get('goal', 'Muscle Gain')
        sets = self._calculate_sets(experience, goal)
        reps = self._calculate_reps(goal, 0.8)
        rest = self._calculate_rest_time(goal, experience)
        return sets, reps, rest

    def _get_optimized_sets(self, profile: dict) -> int:
        """Get optimized number of sets using ML with rule-based validation - HYBRID APPROACH"""
        if self.xgb_sets_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_sets_model.predict(feature_vector.reshape(1, -1))[0]
                sets = int(round(ml_prediction))

                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    sets = min(sets, 4)
                elif experience == 'Intermediate':
                    sets = min(sets, 5)
                else:
                    sets = min(sets, 6)

                if goal == 'Endurance':
                    sets = min(sets, 4)

                sets = max(sets, 2)
                print(f"   🤖 ML optimized sets: {sets}")
                return sets
            except Exception as e:
                print(f"⚠️ ML sets optimization failed: {e}")

        experience = profile.get('experience', 'Beginner')
        goal = profile.get('goal', 'Muscle Gain')
        return self._calculate_sets(experience, goal)

    def _get_optimized_reps(self, profile: dict, intensity: float) -> str:
        """Get optimized rep range using ML with rule-based validation - HYBRID APPROACH"""
        if self.xgb_reps_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_reps_model.predict(feature_vector.reshape(1, -1))[0]
                rep_value = int(round(ml_prediction))
                goal = profile.get('goal', 'Muscle Gain')

                if goal == 'Strength':
                    rep_range = f"{max(1, rep_value - 2)}-{max(rep_value - 1, 3)}"
                elif goal == 'Endurance':
                    rep_range = f"{rep_value + 2}-{rep_value + 6}"
                else:
                    rep_range = f"{max(1, rep_value - 1)}-{rep_value + 3}"

                parts = rep_range.split('-')
                low = int(parts[0])
                high = int(parts[1])

                if goal == 'Strength':
                    low = max(low, 1)
                    high = min(high, 8)
                elif goal == 'Endurance':
                    low = max(low, 12)
                    high = min(high, 20)
                else:
                    low = max(low, 6)
                    high = min(high, 15)

                rep_range = f"{low}-{high}"
                print(f"   🤖 ML optimized reps: {rep_range}")
                return rep_range
            except Exception as e:
                print(f"⚠️ ML reps optimization failed: {e}")

        goal = profile.get('goal', 'Muscle Gain')
        return self._calculate_reps(goal, intensity)

    def _get_optimized_rest_time(self, profile: dict) -> int:
        """Get optimized rest time using ML with rule-based validation - HYBRID APPROACH"""
        if self.xgb_rest_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_rest_model.predict(feature_vector.reshape(1, -1))[0]
                rest_time = int(round(ml_prediction))

                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    rest_time = max(rest_time, 60)
                elif experience == 'Advanced':
                    rest_time = max(rest_time, 30)

                if goal == 'Strength':
                    rest_time = max(rest_time, 120)
                elif goal == 'Endurance':
                    rest_time = min(rest_time, 60)

                rest_time = max(30, min(rest_time, 300))
                print(f"   🤖 ML optimized rest: {rest_time}s")
                return rest_time
            except Exception as e:
                print(f"⚠️ ML rest optimization failed: {e}")

        goal = profile.get('goal', 'Muscle Gain')
        experience = profile.get('experience', 'Beginner')
        return self._calculate_rest_time(goal, experience)

    def _get_optimized_frequency(self, profile: dict) -> int:
        """Get optimized training frequency using ML with rule-based validation - HYBRID APPROACH"""
        if 'days_per_week' in profile and profile.get('days_per_week') is not None:
            return max(1, min(int(profile.get('days_per_week')), 7))

        if self.xgb_frequency_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_frequency_model.predict(feature_vector.reshape(1, -1))[0]

                frequency = int(round(ml_prediction))
                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    frequency = min(frequency, 4)
                elif experience == 'Intermediate':
                    frequency = min(frequency, 5)
                else:
                    frequency = min(frequency, 6)

                if goal == 'Recovery' or goal == 'Maintenance':
                    frequency = min(frequency, 3)

                return max(1, min(frequency, 7))
            except Exception as e:
                print(f"⚠️ ML frequency optimization failed: {e}")

        return profile.get('days_per_week', 4)

    def _get_optimized_progression(self, profile: dict) -> Dict:
        """Get optimized progression timing using ML with rule-based validation - HYBRID APPROACH"""
        if self.xgb_progression_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_progression_model.predict(feature_vector.reshape(1, -1))[0]
                weeks_until_progression = int(max(1, round(ml_prediction)))
                experience = profile.get('experience', 'Beginner')

                if experience == 'Beginner':
                    weeks_until_progression = max(weeks_until_progression, 3)
                elif experience == 'Advanced':
                    weeks_until_progression = min(weeks_until_progression, 2)

                weeks_until_progression = min(weeks_until_progression, 4)

                progression_info = {
                    'weeks_until_next_progression': weeks_until_progression,
                    'progression_method': 'volume_increase' if weeks_until_progression <= 2 else 'intensity_increase'
                }

                print(f"   🤖 ML optimized progression: {progression_info}")
                return progression_info
            except Exception as e:
                print(f"⚠️ ML progression optimization failed: {e}")

        experience = profile.get('experience', 'Beginner')
        return {
            'weeks_until_next_progression': 2 if experience == 'Beginner' else 1,
            'progression_method': 'intensity_increase'
        }

    def _generate_dynamic_split(self, days_per_week: int, goal: str) -> List[str]:
        """Generate workout split based on days and goal - RULE-BASED LOGIC"""
        splits = {
            3: ['Upper Body', 'Lower Body', 'Full Body'],
            4: ['Chest & Triceps', 'Back & Biceps', 'Legs', 'Shoulders & Core'],
            5: ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms'],
            6: ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core'],
            7: ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Active Recovery']
        }

        return splits.get(days_per_week, splits[4])

    def _calculate_rest_days(self, days_per_week: int, profile: dict = None, intensity: float = None) -> List[int]:
        """Calculate optimal rest days in the week using intensity-aware logic"""
        rest_days = 7 - days_per_week

        if rest_days <= 0:
            return []

        if intensity is None:
            intensity = 0.75

        if intensity >= 0.85:
            positions = []
            for i in range(rest_days):
                pos = int(round((i + 1) * 7 / (rest_days + 1))) - 1
                pos = max(0, min(6, pos))
                positions.append(pos)
            unique = []
            for p in positions:
                if p not in unique:
                    unique.append(p)
            while len(unique) < rest_days:
                for p in range(7):
                    if p not in unique:
                        unique.append(p)
                        if len(unique) == rest_days:
                            break
            return sorted(unique)

        if intensity <= 0.65:
            return list(range(7 - rest_days, 7))

        if self.xgb_rest_model is not None and profile is not None:
            try:
                experience = profile.get('experience', 'Beginner')

                if experience == 'Beginner':
                    if rest_days == 1:
                        return [3]
                    elif rest_days == 2:
                        return [2, 5]
                    elif rest_days == 3:
                        return [1, 3, 5]
                    else:
                        return [0, 2, 4, 6]
                elif experience == 'Advanced':
                    if rest_days == 1:
                        return [6]
                    elif rest_days == 2:
                        return [5, 6]
                    else:
                        return [0, 3, 6]
                else:
                    if rest_days == 1:
                        return [3]
                    elif rest_days == 2:
                        return [2, 6]
                    elif rest_days == 3:
                        return [1, 4, 6]
                    else:
                        return [0, 2, 4, 6]

            except Exception as e:
                print(f"⚠️ ML rest day calculation failed: {e}")

        if rest_days == 1:
            return [3]
        elif rest_days == 2:
            return [2, 5]
        elif rest_days == 3:
            return [1, 3, 5]
        elif rest_days == 4:
            return [0, 2, 4, 6]
        else:
            interval = 7 // (rest_days + 1)
            return [i * interval for i in range(1, rest_days + 1)]

    def _create_optimal_schedule(self, weekly_plan: List[Dict], rest_days: List[int]) -> List[Dict]:
        """Create week schedule with rest days - HYBRID APPROACH"""
        schedule = []
        workout_index = 0

        for day in range(7):
            if day in rest_days:
                schedule.append({
                    'day': f'Day {day + 1}',
                    'day_of_week': day,
                    'focus': 'Rest',
                    'exercises': []
                })
            else:
                if workout_index < len(weekly_plan):
                    schedule.append(weekly_plan[workout_index])
                    workout_index += 1

        return schedule

    def _calculate_exercise_count(self, experience: str, goal: str) -> int:
        """Calculate number of exercises per workout - RULE-BASED LOGIC"""
        base_counts = {
            'Beginner': 3,
            'Intermediate': 4,
            'Advanced': 5
        }

        count = base_counts.get(experience, 4)

        if goal == 'Endurance':
            count += 1

        return count

    def _calculate_sets(self, experience: str, goal: str) -> int:
        """Calculate number of sets - RULE-BASED LOGIC"""
        if experience == 'Beginner':
            return 3
        elif experience == 'Intermediate':
            return 4
        else:
            return 5 if goal == 'Muscle Gain' else 4

    def _calculate_reps(self, goal: str, intensity: float) -> str:
        """Calculate rep range based on goal - RULE-BASED LOGIC"""
        if goal == 'Strength':
            return '4-6' if intensity > 0.9 else '5-8'
        elif goal == 'Muscle Gain':
            return '8-12'
        elif goal == 'Endurance':
            return '12-15'
        else:
            return '10-15'

    def _calculate_rest_time(self, goal: str, experience: str) -> int:
        """Calculate rest time between sets - RULE-BASED LOGIC"""
        if goal == 'Strength':
            return 180 if experience == 'Advanced' else 120
        elif goal == 'Muscle Gain':
            return 90 if experience == 'Advanced' else 60
        elif goal == 'Endurance':
            return 45
        else:
            return 30

    def _adjust_reps_for_intensity(self, base_reps: str, intensity: float) -> str:
        """Adjust reps based on intensity - RULE-BASED LOGIC"""
        if intensity < 0.7:
            return base_reps

        parts = base_reps.split('-')
        if len(parts) == 2:
            low = int(parts[0])
            high = int(parts[1])

            if intensity > 0.9:
                low = max(low - 2, 1)
                high = max(high - 2, low + 2)

            return f"{low}-{high}"

        return base_reps

    def _estimate_reps_avg(self, reps_range: str) -> float:
        """Estimate avg reps from a range string like '8-12'"""
        try:
            parts = str(reps_range).split('-')
            if len(parts) == 2:
                low = float(parts[0])
                high = float(parts[1])
                return (low + high) / 2.0
            return float(parts[0])
        except Exception:
            return 10.0

    def _apply_age_based_caps(self, profile: dict, sets: int, reps: str, rest_time: int, intensity: float) -> tuple:
        """Apply age-based safety caps to workout parameters - RULE-BASED SAFETY LOGIC"""
        try:
            age = int(float(profile.get('age', 30)))
        except Exception:
            age = 30

        # Log initial values before applying rules
        print(f"   📋 Age-based safety check: age={age}, initial sets={sets}, reps='{reps}', rest={rest_time}s, intensity={intensity:.2f}")

        # Apply age-appropriate limits
        if age > 65:
            # For older adults, reduce intensity and volume
            original_intensity = intensity
            original_sets = sets
            original_rest = rest_time

            intensity = min(intensity, 0.7)
            sets = min(sets, 3)
            rest_time = max(rest_time, 90)  # More rest for recovery

            # Adjust reps to safer range for older adults
            try:
                low, high = map(int, reps.split('-'))
                low = max(low, 8)  # Minimum of 8 reps to avoid heavy loads
                high = min(high, 15)  # Maximum of 15 reps
                reps = f"{low}-{high}"
            except ValueError:
                # Handle cases where reps is not in x-y format
                print(f"   ⚠️ Reps format not recognized: '{reps}', using default safe range")
                reps = "10-15"

            # Log changes applied by rules
            if original_intensity != intensity or original_sets != sets or original_rest != rest_time:
                print(f"   ✅ Applied senior safety rules: intensity {original_intensity:.2f}->{intensity:.2f}, sets {original_sets}->{sets}, rest {original_rest}s->{rest_time}s")

        elif age < 18:
            # For younger individuals, focus on form over heavy loads
            original_intensity = intensity
            original_sets = sets

            intensity = min(intensity, 0.8)
            sets = min(sets, 4)

            # Higher rep ranges for skill development
            try:
                low, high = map(int, reps.split('-'))
                low = max(low, 10)
                high = min(high, 20)
                reps = f"{low}-{high}"
            except ValueError:
                # Handle cases where reps is not in x-y format
                print(f"   ⚠️ Reps format not recognized: '{reps}', using default safe range")
                reps = "12-15"

            # Log changes applied by rules
            if original_intensity != intensity or original_sets != sets:
                print(f"   ✅ Applied youth safety rules: intensity {original_intensity:.2f}->{intensity:.2f}, sets {original_sets}->{sets}")

        else:
            print(f"   ✅ No age-based adjustments needed for age {age}")

        return sets, reps, rest_time, intensity

    def _filter_biomechanics(self, exercises: pd.DataFrame, profile: dict) -> pd.DataFrame:
        """Filter exercises based on biomechanical safety - RULE-BASED SAFETY LOGIC"""
        if exercises.empty:
            return exercises

        try:
            print(f"   📋 Applying biomechanical safety filters...")

            original_count = len(exercises)
            experience = profile.get('experience', 'Beginner')
            try:
                age = int(float(profile.get('age', 30)))
            except Exception:
                age = 30

            # For beginners, filter out complex movements
            if experience == 'Beginner' and 'Name' in exercises.columns:
                # Avoid overly complex exercises for beginners
                complex_exercises_keywords = ['Olympic lift', 'Clean and jerk', 'Snatch', 'Advanced', 'Plyometric']

                for keyword in complex_exercises_keywords:
                    exercises = exercises[
                        ~exercises['Name'].str.contains(keyword, case=False, na=False)
                    ]

            # Use Check_Type column if available (e.g., filter out cardio for strength-focused plans)
            if 'Check_Type' in exercises.columns:
                goal = profile.get('goal', 'Muscle Gain')

                # For strength-focused goals, prioritize strength exercises
                if goal == 'Strength' and 'strength' in exercises['Check_Type'].values:
                    exercises = exercises[exercises['Check_Type'] == 'strength']
                elif goal == 'Endurance' and 'cardio' in exercises['Check_Type'].values:
                    # For endurance-focused goals, include more cardio exercises
                    pass  # Allow all types but this could be expanded

            # Use Risk_Level column if available (assuming lower risk is better for beginners)
            if 'Risk_Level' in exercises.columns:
                risk_mapping = {'Low': 1, 'Medium': 2, 'High': 3}

                if experience == 'Beginner':
                    # Filter out high-risk exercises for beginners
                    exercises = exercises[
                        exercises['Risk_Level'].map(risk_mapping).fillna(2) <= 2
                    ]  # Allow Low and Medium risk
                elif age > 65:
                    # For seniors, only allow low-risk exercises
                    exercises = exercises[
                        exercises['Risk_Level'].map(risk_mapping).fillna(1) <= 1
                    ]  # Only Low risk
            else:
                # If Risk_Level column doesn't exist, create a basic risk assessment based on other factors
                print(f"   ℹ️ Risk_Level column not found, using basic heuristics for safety")

            # Additional biomechanical filters based on age
            if age > 65:
                # Avoid high-impact exercises for seniors
                high_impact_keywords = ['jump', 'plyo', 'explosive', 'sprint']
                for keyword in high_impact_keywords:
                    exercises = exercises[
                        ~exercises['Name'].str.contains(keyword, case=False, na=False)
                    ]

            # Log the results of biomechanical filtering
            filtered_count = len(exercises)
            if original_count != filtered_count:
                print(f"   ✅ Applied biomechanical filters: {original_count} -> {filtered_count} exercises")
            else:
                print(f"   ✅ No biomechanical filters applied, kept all {original_count} exercises")

            return exercises

        except Exception as e:
            print(f"⚠️ Error in biomechanics filtering: {e}")
            return exercises

    def _infer_rest_days_count(self, profile: dict, intensity: float, sets: int, reps: str, num_exercises: int) -> int:
        """Decide rest days based on weekly load + profile (MODEL-DRIVEN LOGIC)"""
        reps_avg = self._estimate_reps_avg(reps)
        weekly_load = intensity * sets * reps_avg * num_exercises * 7

        if weekly_load >= 300:
            rest_days = 3
        elif weekly_load >= 220:
            rest_days = 2
        elif weekly_load >= 150:
            rest_days = 1
        else:
            rest_days = 0

        experience = profile.get('experience', 'Beginner')
        goal = profile.get('goal', 'Muscle Gain')
        streak = profile.get('streak', 0)
        consistency = profile.get('consistency', 0.7)

        if experience == 'Beginner':
            rest_days += 1
        elif experience == 'Advanced':
            rest_days -= 1

        if goal in ['Strength', 'Recovery']:
            rest_days += 1
        if goal == 'Endurance':
            rest_days -= 1

        if streak >= 10 and consistency >= 0.8:
            rest_days -= 1

        return max(0, min(3, rest_days))

    def generate_weekly_plan(self, profile: dict) -> List[Dict]:
        """Generate a complete weekly workout plan - HYBRID APPROACH WITH RULE-BASED SAFETY"""

        goal = profile.get('goal', 'Muscle Gain')
        experience = profile.get('experience', 'Beginner')
        equipment = profile.get('equipment', [])
        body_issues = profile.get('body_issues', [])

        intensity = self._get_intensity_adjustment(profile)
        print(f"   Intensity: {intensity:.2f}")

        sets = self._get_optimized_sets(profile)
        reps = self._get_optimized_reps(profile, intensity)
        rest_time = self._get_optimized_rest_time(profile)

        # Explicit rule-based validation after ML
        print(f"   🤖 ML outputs before rule validation: sets={sets}, reps='{reps}', rest={rest_time}s, intensity={intensity:.2f}")
        sets, reps, rest_time, intensity = self._apply_age_based_caps(profile, sets, reps, rest_time, intensity)
        print(f"   ✅ Final values after rule validation: sets={sets}, reps='{reps}', rest={rest_time}s, intensity={intensity:.2f}")

        # Log the safety validation process
        print(f"   🛡️ Hybrid system: ML personalization guided by rule-based safety checks")

        num_exercises = self._calculate_exercise_count(experience, goal)

        # Use ML-optimized frequency when available, otherwise fall back to calculated frequency
        ml_optimized_frequency = self._get_optimized_frequency(profile)
        days_per_week = ml_optimized_frequency

        rest_days_count = 7 - days_per_week

        print(f"\n🎯 Generating workout plan:")
        print(f"   Days: {days_per_week}")
        print(f"   Goal: {goal}")
        print(f"   Experience: {experience}")
        print(f"   Equipment: {equipment}")
        print(f"   Body Issues: {body_issues}")

        split = self._get_optimized_workout_split(profile, days_per_week)
        print(f"   Split: {split}")

        available_exercises = self.exercises_df.copy()
        available_exercises = self.filter_by_equipment(available_exercises, equipment)
        available_exercises = self.filter_by_injuries(available_exercises, body_issues)

        # Biomechanics filter (rule-based safety)
        available_exercises = self._filter_biomechanics(available_exercises, profile)

        # Compute progression info once for the entire plan
        progression_info = self._get_optimized_progression(profile)
        print(f"   📈 Progression info for entire plan: {progression_info}")

        rest_days = self._calculate_rest_days(days_per_week, profile, intensity)
        rest_day_set = set(rest_days)

        weekly_plan = []
        workout_day_idx = 0

        for day_num in range(7):
            if day_num in rest_day_set:
                day_plan = {
                    'day': f'Day {day_num + 1}',
                    'day_of_week': day_num,
                    'focus': 'Rest Day',
                    'exercises': [],
                    'intensity': 0.0,
                    'type': 'rest'
                }
                print(f"\n   Day {day_num + 1}: Rest Day")
            else:
                focus = split[workout_day_idx % len(split)]
                workout_day_idx += 1

                print(f"\n   Day {day_num + 1}: {focus}")

                if focus == 'Full Body':
                    day_exercises = available_exercises
                elif focus == 'Upper Body':
                    day_exercises = available_exercises[
                        available_exercises['Target_Muscle'].isin(['Chest', 'Back', 'Shoulders', 'Arms'])
                    ]
                elif focus == 'Lower Body':
                    day_exercises = available_exercises[
                        available_exercises['Target_Muscle'].isin(['Legs'])
                    ]
                else:
                    target_muscles = []
                    if 'Chest' in focus:
                        target_muscles.append('Chest')
                    if 'Back' in focus:
                        target_muscles.append('Back')
                    if 'Legs' in focus:
                        target_muscles.append('Legs')
                    if 'Shoulders' in focus:
                        target_muscles.append('Shoulders')
                    if 'Arms' in focus or 'Biceps' in focus or 'Triceps' in focus:
                        target_muscles.append('Arms')
                    if 'Core' in focus:
                        target_muscles.append('Core')

                    if target_muscles:
                        day_exercises = available_exercises[
                            available_exercises['Target_Muscle'].isin(target_muscles)
                        ]
                    else:
                        day_exercises = available_exercises

                if len(day_exercises) == 0:
                    print(f"      ⚠️ No exercises found for {focus}, using all")
                    day_exercises = available_exercises

                selected = day_exercises.head(num_exercises)

                exercises = []
                for idx, row in selected.iterrows():
                    validated_sets = min(sets, 6) if experience != 'Beginner' else min(sets, 4)
                    validated_rest = max(rest_time, 30)

                    exercises.append({
                        'id': f"{focus.lower().replace(' ', '-')}-{idx}",
                        'name': row['Name'],
                        'sets': validated_sets,
                        'reps': reps,
                        'rest': validated_rest,
                        'target': row['Target_Muscle'],
                        'equipment': row['Equipment']
                    })

                print(f"      ✅ Selected {len(exercises)} exercises")

                day_plan = {
                    'day': f'Day {day_num + 1}',
                    'day_of_week': day_num,
                    'focus': focus,
                    'exercises': exercises,
                    'intensity': intensity,
                    'type': 'workout'
                }

            day_plan['progression_info'] = progression_info
            weekly_plan.append(day_plan)

        if len(weekly_plan) != 7:
            print(f"⚠️ Warning: Expected 7 days but got {len(weekly_plan)}. Creating missing days.")
            while len(weekly_plan) < 7:
                day_num = len(weekly_plan)
                weekly_plan.append({
                    'day': f'Day {day_num + 1}',
                    'day_of_week': day_num,
                    'focus': 'Rest Day',
                    'exercises': [],
                    'intensity': 0.0,
                    'type': 'rest',
                    'progression_info': progression_info
                })

        print(f"\n✅ Generated full 7-day weekly plan with {days_per_week} workout days and {7 - days_per_week} rest days")
        return weekly_plan


_workout_engine = None

def get_workout_engine():
    global _workout_engine
    if _workout_engine is None:
        _workout_engine = WorkoutEngine()
    return _workout_engine