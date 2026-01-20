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
            
            if os.path.exists(nut_path):
                self.nutrition_df = pd.read_csv(nut_path)
                self.nutrition_df["veg_nonveg"] = self.nutrition_df["veg_nonveg"].astype(str).str.lower().str.strip()
                self.nutrition_df["allergic_ingredients"] = self.nutrition_df["allergic_ingredients"].fillna("")

        except Exception as e:
            print(f"❌ Error loading CSV data: {e}")

    def predict_difficulty(self, user_profile):
        if not self.model: return "Beginner"
        try:
            input_data = pd.DataFrame([{
                "age": user_profile["age"],
                "weight": user_profile["weight"],
                "height": user_profile["height"],
                "gender_n": self.le_gender.transform([user_profile["gender"]])[0],
                "goal_n": self.le_goal.transform([user_profile["goal"]])[0],
            }])
            pred_idx = self.model.predict(input_data)[0]
            return self.le_target.inverse_transform([pred_idx])[0]
        except: return "Beginner"

    def recommend_workout(self, user_profile, available_equipment=[]):
        if self.exercises_df is None: return self._get_fallback_workout()

        ai_level = self.predict_difficulty(user_profile)
        user_equip = [str(e).lower().strip() for e in available_equipment]

        def is_equipment_available(equip_str):
            equip_str = str(equip_str).lower()
            if "body" in equip_str or "none" in equip_str or "assisted" in equip_str: return True
            for u_e in user_equip:
                if u_e in equip_str or equip_str in u_e: return True
            return False

        candidates = self.exercises_df[self.exercises_df["equipment"].apply(is_equipment_available)]
        if candidates.empty:
            candidates = self.exercises_df[self.exercises_df["equipment"].str.contains("body", case=False, na=False)]

        plan = []
        targets = ["warm up", "chest", "back", "legs", "shoulders", "abs", "arms", "cardio"]

        for part in targets:
            if part == "warm up":
                part_exercises = candidates[candidates["body_part"].astype(str).str.contains("cardio|stretch", case=False, na=False)]
            elif part == "abs":
                part_exercises = candidates[candidates["body_part"].astype(str).str.contains("waist|abs|core", case=False, na=False)]
            else:
                part_exercises = candidates[candidates["body_part"].astype(str).str.contains(part, case=False, na=False)]

            if not part_exercises.empty:
                ex = part_exercises.sample(1).iloc[0].to_dict()
                ex["sets"] = 3
                ex["reps"] = "10-12"
                ex["completed_sets"] = 0
                ex["is_done"] = False
                plan.append(ex)

        if len(plan) < 3: return self._get_fallback_workout()
        return plan

    def recommend_meals(self, goal, diet_preference, allergies=[]):
        if self.nutrition_df is None: return self._get_fallback_meals()
        df = self.nutrition_df.copy()
        diet = str(diet_preference).lower()

        if "veg" in diet and "non" not in diet:
            df = df[df["veg_nonveg"] == "veg"]
        
        def get_meal_item(dataframe, count=1):
            if dataframe.empty: return []
            items = dataframe.sample(n=min(count, len(dataframe))).replace({np.nan: None}).to_dict(orient="records")
            for item in items:
                item["name"] = item["food_name"]
                item["calories"] = int(item["calories_100g"])
                item["protein"] = int(item["protein_100g"])
                item["quantity"] = "1 serving (100g)"
            return items

        return {
            "breakfast": get_meal_item(df, 2),
            "lunch": get_meal_item(df, 2),
            "dinner": get_meal_item(df, 2)
        }

    # --- NEW: SWAP LOGIC ---
    def get_similar_food(self, old_name, target_cal):
        if self.nutrition_df is None: return {}
        df = self.nutrition_df.copy()
        
        # Find food with similar calories (+/- 100)
        candidates = df[
            (df['calories_100g'] >= target_cal - 100) & 
            (df['calories_100g'] <= target_cal + 100) & 
            (df['food_name'] != old_name)
        ]
        
        if candidates.empty: candidates = df 
        item = candidates.sample(1).iloc[0].to_dict()
        
        return {
            "name": item["food_name"],
            "calories": int(item["calories_100g"]),
            "protein": int(item["protein_100g"]),
            "quantity": "1 Alternative Serving"
        }

    def _get_fallback_workout(self):
        return [{"name": "Push Up", "sets": 3, "reps": "10", "body_part": "Chest"}]

    def _get_fallback_meals(self):
        return {"breakfast": [], "lunch": [], "dinner": []}

ml_service = MLService()