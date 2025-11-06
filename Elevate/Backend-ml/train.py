import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
import joblib
import os

# --- Configuration ---
DATA_DIR = "data"
MODELS_DIR = "models"
NUTRITION_IN_FILE = os.path.join(DATA_DIR, "nutrition.csv")
EXERCISE_IN_FILE = os.path.join(DATA_DIR, "fitness_exercises.csv")

NUTRITION_OUT_FILE = os.path.join(DATA_DIR, "nutrition_processed.csv")
EXERCISE_OUT_FILE = os.path.join(DATA_DIR, "fitness_exercises_processed.csv")

MEAL_MODEL_FILE = os.path.join(MODELS_DIR, "meal_model.joblib")
MEAL_ENCODER_FILE = os.path.join(MODELS_DIR, "meal_encoder.joblib")

WORKOUT_MODEL_FILE = os.path.join(MODELS_DIR, "workout_model.joblib")
WORKOUT_ENCODER_FILE = os.path.join(MODELS_DIR, "workout_encoders.joblib")


# ------------------ Nutrition Data Cleaning ------------------
def clean_nutrition_data(df):
    """Cleans and engineers features for the nutrition dataset."""
    print("Cleaning nutrition data...")

    # Select relevant columns (✅ corrected column name)
    cols_to_use = ['name', 'calories', 'protein', 'fat', 'carbohydrate']
    df = df[cols_to_use]

    # Clean non-numeric values (like 't' or 'g')
    for col in ['calories', 'protein', 'fat', 'carbohydrate']:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("g", "", regex=False)
            .str.replace("mg", "", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop missing values
    df = df.dropna().reset_index(drop=True)

    # --- Feature Engineering: Add "goal" column ---
    def assign_goal(row):
        protein_g = row['protein']
        carbs_g = row['carbohydrate']
        fat_g = row['fat']
        calories = row['calories']

        # High protein, moderate calories
        if protein_g > 15 and calories < 400:
            return "Muscle Gain"
        # Low calorie, low fat
        elif calories < 200 and fat_g < 10:
            return "Weight Loss"
        # Balanced macros
        elif 10 < protein_g < 20 and 20 < carbs_g < 40 and calories < 500:
            return "Maintain"
        else:
            return "General"

    df['goal'] = df.apply(assign_goal, axis=1)

    # Keep only goal-specific foods
    df = df[df['goal'] != 'General'].reset_index(drop=True)

    print(f"Nutrition data cleaned. {len(df)} goal-oriented items found.")
    return df


# ------------------ Meal Model Training ------------------
def train_meal_model(df):
    """Trains an XGBoost classifier for meal recommendations."""
    print("Training meal model...")

    X = df[['calories', 'protein', 'fat', 'carbohydrate']]
    y = df['goal']

    # Encode target labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = XGBClassifier(
        objective="multi:softmax",
        num_class=len(le.classes_),
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
        n_estimators=200,
        learning_rate=0.1,
        max_depth=4
    )

    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    print(f"✅ Meal model accuracy: {acc:.2f}")

    # Save model and encoder
    joblib.dump(model, MEAL_MODEL_FILE)
    joblib.dump(le, MEAL_ENCODER_FILE)
    print("Meal model and encoder saved.")


# ------------------ Exercise Data Cleaning ------------------
def clean_exercise_data(df):
    """Cleans and engineers features for the exercise dataset."""
    print("Cleaning exercise data...")
    cols_to_use = ['name', 'bodyPart', 'equipment', 'target']
    df = df[cols_to_use]
    df = df.dropna().reset_index(drop=True)

    # Add difficulty level
    def assign_difficulty(row):
        equipment = row['equipment']
        if equipment in ['barbell', 'dumbbell', 'cable', 'machine', 'olympic barbell', 'ez barbell']:
            return "Intermediate"
        elif equipment == 'body weight':
            return "Beginner"
        else:
            return "Advanced"  # e.g. kettlebell, sled, resistance band

    df['difficulty'] = df.apply(assign_difficulty, axis=1)
    print(f"Exercise data cleaned. {len(df)} items found.")
    return df


# ------------------ Workout Model Training ------------------
def train_workout_model(df):
    """Trains a Decision Tree model for workout difficulty classification."""
    print("Training workout model...")

    features = ['bodyPart', 'equipment']
    target = 'difficulty'

    encoders = {}
    df_encoded = df.copy()

    for col in features + [target]:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        encoders[col] = le

    X = df_encoded[features]
    y = df_encoded[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    print(f"✅ Workout model accuracy: {acc:.2f}")

    joblib.dump(model, WORKOUT_MODEL_FILE)
    joblib.dump(encoders, WORKOUT_ENCODER_FILE)
    print("Workout model and encoders saved.")


# ------------------ Main Function ------------------
def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- Nutrition Data ---
    try:
        df_nutrition = pd.read_csv(NUTRITION_IN_FILE)
        df_nutrition_clean = clean_nutrition_data(df_nutrition)
        train_meal_model(df_nutrition_clean)
        df_nutrition_clean.to_csv(NUTRITION_OUT_FILE, index=False)
        print(f"Processed nutrition data saved to {NUTRITION_OUT_FILE}")
    except FileNotFoundError:
        print(f"❌ ERROR: {NUTRITION_IN_FILE} not found.")
    except Exception as e:
        print(f"❌ An error occurred during nutrition processing: {e}")

    print("-" * 30)

    # --- Exercise Data ---
    try:
        df_exercise = pd.read_csv(EXERCISE_IN_FILE)
        df_exercise_clean = clean_exercise_data(df_exercise)
        train_workout_model(df_exercise_clean)
        df_exercise_clean.to_csv(EXERCISE_OUT_FILE, index=False)
        print(f"Processed exercise data saved to {EXERCISE_OUT_FILE}")
    except FileNotFoundError:
        print(f"❌ ERROR: {EXERCISE_IN_FILE} not found.")
    except Exception as e:
        print(f"❌ An error occurred during exercise processing: {e}")

    print("\n🎉 Training complete! You can now run the FastAPI server with:")
    print("👉 uvicorn main:app --reload")


if __name__ == "__main__":
    main()
