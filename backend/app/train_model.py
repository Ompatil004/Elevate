import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Ensure models directory exists
if not os.path.exists("app/models"):
    os.makedirs("app/models")

print("🚀 Starting AI Training Process...")

# ==========================================
# 1. GENERATE TRAINING DATA (Simulated)
# ==========================================
# We simulate 5000 users to teach the model patterns
# e.g., High BMI + Beginner = Low Intensity
# e.g., Low Age + Muscle Gain = High Intensity

data_size = 5000
np.random.seed(42)

data = {
    'age': np.random.randint(18, 60, data_size),
    'gender': np.random.choice(['Male', 'Female'], data_size),
    'weight': np.random.randint(50, 120, data_size), # kg
    'height': np.random.randint(150, 200, data_size), # cm
    'goal': np.random.choice(['Muscle Gain', 'Weight Loss', 'Maintain'], data_size),
}

df = pd.DataFrame(data)

# Calculate Logic for "Correct" Labels (The Teacher)
def determine_intensity(row):
    bmi = row['weight'] / ((row['height']/100) ** 2)
    score = 0
    
    # Age factor
    if row['age'] < 30: score += 2
    elif row['age'] < 50: score += 1
    
    # BMI factor
    if 18.5 < bmi < 25: score += 2 # Healthy weight
    elif bmi > 30: score -= 1 # Obese (needs caution)
    
    # Goal factor
    if row['goal'] == 'Muscle Gain': score += 2
    
    # Final Classification
    if score >= 4: return 'Advanced'
    elif score >= 2: return 'Intermediate'
    else: return 'Beginner'

df['recommended_level'] = df.apply(determine_intensity, axis=1)

print("✔ Generated 5,000 synthetic user profiles for training.")

# ==========================================
# 2. PREPROCESS DATA
# ==========================================
# Convert text to numbers (XGBoost only understands numbers)

le_gender = LabelEncoder()
le_goal = LabelEncoder()
le_target = LabelEncoder()

df['gender_n'] = le_gender.fit_transform(df['gender'])
df['goal_n'] = le_goal.fit_transform(df['goal'])
y = le_target.fit_transform(df['recommended_level'])

X = df[['age', 'weight', 'height', 'gender_n', 'goal_n']]

# ==========================================
# 3. TRAIN XGBOOST MODEL
# ==========================================

print("🧠 Training XGBoost Classifier...")

model = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    use_label_encoder=False,
    eval_metric='mlogloss'
)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# Accuracy Check
acc = model.score(X_test, y_test)
print(f"🏆 Model Trained! Accuracy: {acc*100:.2f}%")

# ==========================================
# 4. SAVE ARTIFACTS
# ==========================================
# We need to save the model AND the encoders to use them in the real app

joblib.dump(model, "app/models/xgb_workout.pkl")
joblib.dump(le_gender, "app/models/le_gender.pkl")
joblib.dump(le_goal, "app/models/le_goal.pkl")
joblib.dump(le_target, "app/models/le_target.pkl")

print("💾 Model & Encoders saved to 'backend/app/models/'")