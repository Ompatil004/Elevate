import pandas as pd
import numpy as np
import os
import joblib

# Robust Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
MODEL_DIR = os.path.join(BASE_DIR, "models")


class MLService:
    def __init__(self):
        self.exercises_df = None
        self.nutrition_df = None
        self.load_data()
        self.load_model()

    def load_model(self):
        try:
            self.model = joblib.load(os.path.join(MODEL_DIR, "xgb_workout.pkl"))
            self.le_gender = joblib.load(os.path.join(MODEL_DIR, "le_gender.pkl"))
            self.le_goal = joblib.load(os.path.join(MODEL_DIR, "le_goal.pkl"))
            self.le_target = joblib.load(os.path.join(MODEL_DIR, "le_target.pkl"))
            print("✔ XGBoost Model Loaded Successfully")
        except:
            print("⚠ Warning: XGBoost model not found. Using fallback logic.")
            self.model = None

    def load_data(self):
        print(f"📂 Loading datasets from: {DATA_DIR}")
        try:
            ex_path = os.path.join(DATA_DIR, "home_exercises.csv")
            nut_path = os.path.join(DATA_DIR, "indian_food_nutrition_100g.csv")

            if os.path.exists(ex_path):
                self.exercises_df = pd.read_csv(ex_path)
                self.exercises_df.columns = self.exercises_df.columns.str.lower()
                self.exercises_df = self.exercises_df.rename(columns={"exercise_name": "name"})
                print(f"   - Loaded {len(self.exercises_df)} exercises")
            else:
                print(f"❌ FILE NOT FOUND: {ex_path}")

            if os.path.exists(nut_path):
                self.nutrition_df = pd.read_csv(nut_path)
                self.nutrition_df["veg_nonveg"] = (
                    self.nutrition_df["veg_nonveg"].astype(str).str.lower().str.strip()
                )
                self.nutrition_df["allergic_ingredients"] = self.nutrition_df[
                    "allergic_ingredients"
                ].fillna("")
                print(f"   - Loaded {len(self.nutrition_df)} food items")
            else:
                print(f"❌ FILE NOT FOUND: {nut_path}")

        except Exception as e:
            print(f"❌ Error loading CSV data: {e}")

    # ... inside MLService class ...
    def get_similar_food(self, old_name, target_cal):
        if self.nutrition_df is None: return {}
        
        df = self.nutrition_df.copy()
        
        # Find foods with similar calories (+/- 100) but NOT the same name
        candidates = df[
            (df['calories_100g'] >= target_cal - 100) & 
            (df['calories_100g'] <= target_cal + 100) & 
            (df['food_name'] != old_name)
        ]
        
        if candidates.empty:
            candidates = df # Fallback if nothing specific found
            
        item = candidates.sample(1).iloc[0].to_dict()
        
        return {
            "name": item["food_name"],
            "calories": int(item["calories_100g"]),
            "protein": int(item["protein_100g"]),
            "quantity": "1 Alternative Portion"
        }
    
    def predict_difficulty(self, user_profile):
        if not self.model:
            return "Beginner"
        try:
            input_data = pd.DataFrame([
                {
                    "age": user_profile["age"],
                    "weight": user_profile["weight"],
                    "height": user_profile["height"],
                    "gender_n": self.le_gender.transform([user_profile["gender"]])[0],
                    "goal_n": self.le_goal.transform([user_profile["goal"]])[0],
                }
            ])
            pred_idx = self.model.predict(input_data)[0]
            return self.le_target.inverse_transform([pred_idx])[0]
        except:
            return "Beginner"

    def recommend_workout(self, user_profile, available_equipment=[]):
        if self.exercises_df is None: return []

        # 1. AI Difficulty Prediction
        ai_level = self.predict_difficulty(user_profile)
        user_equip = [str(e).lower().strip() for e in available_equipment]

        # 2. Filter Equipment (Bidirectional Match)
        # Fixes "Dumbbells" (User) vs "Dumbbell" (CSV) mismatch
        def is_equipment_available(equip_str):
            equip_str = str(equip_str).lower()
            # Always allow basic stuff
            if "body" in equip_str or "none" in equip_str or "assisted" in equip_str:
                return True
            
            for u_e in user_equip:
                # Check if User equip is inside CSV string OR CSV string is inside User equip
                if u_e in equip_str or equip_str in u_e:
                    return True
            return False

        candidates = self.exercises_df[
            self.exercises_df["equipment"].apply(is_equipment_available)
        ]

        # Fallback: If no match, force Bodyweight
        if candidates.empty:
            print("⚠ No equipment match found. Using Bodyweight.")
            candidates = self.exercises_df[
                self.exercises_df["equipment"].str.contains("body", case=False, na=False)
            ]

        plan = []
        # Updated Targets to match standard CSV names better
        # Changed 'waist' -> 'abs|core', added 'shoulders'
        targets = ["warm up", "chest", "back", "legs", "shoulders", "abs", "arms", "cardio"]

        for part in targets:
            # Flexible Regex Matching
            if part == "warm up":
                part_exercises = candidates[candidates["body_part"].astype(str).str.contains("cardio|stretch", case=False, na=False)]
            elif part == "abs":
                 part_exercises = candidates[candidates["body_part"].astype(str).str.contains("waist|abs|core", case=False, na=False)]
            else:
                part_exercises = candidates[candidates["body_part"].astype(str).str.contains(part, case=False, na=False)]

            if not part_exercises.empty:
                ex = part_exercises.sample(1).iloc[0].to_dict()
                name = ex["name"].lower()

                # --- SMART REPS ---
                if "plank" in name or "hold" in name:
                    ex["sets"] = 3; ex["reps"] = "30-45 sec"
                elif "stretch" in name or "yoga" in name:
                    ex["sets"] = 2; ex["reps"] = "60 sec"
                elif "cardio" in str(ex["body_part"]).lower():
                    ex["sets"] = 1; ex["reps"] = "10-15 mins"
                elif user_profile.get("goal") == "Maintenance":
                    ex["sets"] = 3; ex["reps"] = "12-15"
                elif user_profile.get("goal") == "Muscle Gain":
                    ex["sets"] = 4; ex["reps"] = "8-10"
                else:
                    ex["sets"] = 3; ex["reps"] = "15-20"

                ex["completed_sets"] = 0
                ex["is_done"] = False
                plan.append(ex)

        # FINAL SAFETY: If plan is still empty, manually add pushups so dashboard isn't empty
        if len(plan) == 0:
            return [{"name": "Push Up", "body_part": "Chest", "sets": 3, "reps": "10", "completed_sets": 0, "is_done": False}]

        return plan

    def recommend_meals(self, goal, diet_preference, allergies=[], calorie_target=2000):
        if self.nutrition_df is None:
            return {"breakfast": [], "lunch": [], "dinner": []}

        df = self.nutrition_df.copy()
        diet = str(diet_preference).lower()

        # 1. Veg/Non-Veg/Both Logic
        if "both" in diet or "mix" in diet:
            pass  # Do not filter, allow everything
        elif "non" in diet:
             # Usually non-veg eaters also eat veg, so we keep everything
             # If you want STRICTLY meat, uncomment next line:
             # df = df[df['veg_nonveg'] == 'non-veg']
             pass
        elif "veg" in diet:
            # Strict Vegetarian
            df = df[df["veg_nonveg"] == "veg"]
        elif "vegan" in diet:
             # Simplistic Vegan Filter (removes known dairy/meat)
             df = df[df["veg_nonveg"] == "veg"]
             df = df[~df["food_name"].str.contains("Milk|Curd|Paneer|Ghee|Butter|Cheese|Honey", case=False)]

        # 2. Strict Allergy Filtering
        if "Gluten" in allergies:
            df = df[~df["food_name"].str.contains("Wheat|Maida|Semolina|Roti|Bread", case=False, na=False)]
        if "Lactose Intolerant" in allergies:
            df = df[~df["food_name"].str.contains("Milk|Curd|Paneer|Cheese|Butter|Ghee", case=False, na=False)]
        if "Nuts" in allergies:
            df = df[~df["allergic_ingredients"].str.contains("nut|almond|cashew|walnut|peanut", case=False, na=False)]
        if "Diabetes" in allergies:
            df = df[df["sugar_100g"] < 5]

        # 3. Sort by Goal
        if goal == "Muscle Gain":
            df = df.sort_values(by="protein_100g", ascending=False)
        elif goal == "Weight Loss":
            df = df.sort_values(by="calories_100g", ascending=True)
        else:
            # Maintenance: Random / Balanced
            df = df.sample(frac=1)

        # 4. Generate Structure
        def get_meal_item(dataframe, count=1, meal_type="General"):
            items = (
                dataframe.sample(n=min(count, len(dataframe)))
                .replace({np.nan: None})
                .to_dict(orient="records")
            )
            for item in items:
                item["quantity"] = "1 serving (100g)"
                if meal_type == "Breakfast" and item["calories_100g"] > 300:
                    item["quantity"] = "Small portion (50g)"
                elif meal_type == "Lunch":
                    item["quantity"] = "1 full bowl (150g)"
                
                # Frontend Formatting
                item["name"] = item["food_name"]
                item["calories"] = item["calories_100g"]
                item["protein"] = item["protein_100g"]
                item["carbs"] = item.get("carbohydrates_100g", 0) # Safety
                item["fats"] = item.get("fat_100g", 0) # Safety
                item["is_eaten"] = False
            return items

        # Prevent crash if df is empty after filtering
        if df.empty:
             print("⚠ Warning: No food items match filters! Returning empty.")
             return {"breakfast": [], "lunch": [], "dinner": []}

        breakfast = get_meal_item(df.head(20), 2, "Breakfast")
        lunch = get_meal_item(df.iloc[20:50], 2, "Lunch")
        dinner = get_meal_item(df.head(30), 2, "Dinner")

        return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner}

# Initialize at the end
ml_service = MLService()