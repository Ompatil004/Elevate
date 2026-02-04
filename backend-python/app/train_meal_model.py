import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_meal_model():
    """Train XGBoost model for meal recommendations"""
    
    print("=" * 60)
    print("🍽️ TRAINING XGBOOST MEAL RECOMMENDATION MODEL")
    print("=" * 60)
    
    # Create models directory if not exists
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Load nutrition data
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nutrition_path = os.path.join(base_dir, 'data', 'nutrition_processed.csv')
    
    print(f"\n📊 Loading nutrition data from: {nutrition_path}")
    
    if not os.path.exists(nutrition_path):
        print(f"❌ ERROR: Nutrition data not found at {nutrition_path}")
        return
    
    df = pd.read_csv(nutrition_path)
    print(f"✅ Loaded {len(df)} meal items")
    
    # Create synthetic training data for meal recommendations
    print("\n🔄 Creating synthetic training data...")
    
    # Create features
    np.random.seed(42)
    n_samples = 1000
    
    # Simulate user profiles
    goals = ['Weight Loss', 'Fat Loss', 'Muscle Gain', 'Maintenance', 'Athletic Performance']
    intensities = ['high', 'moderate', 'low', 'rest']
    
    # Generate training data
    training_data = []
    
    for _ in range(n_samples):
        # User target macros
        target_calories = np.random.randint(1500, 3000)
        target_protein = np.random.randint(100, 200)
        target_carbs = np.random.randint(150, 300)
        target_fat = np.random.randint(40, 80)
        
        # Meal macros (from actual data)
        if len(df) > 0:
            meal = df.sample(1).iloc[0]
            meal_calories = meal.get('calories', np.random.randint(200, 600))
            meal_protein = meal.get('protein', np.random.randint(10, 50))
            meal_carbs = meal.get('carbs', np.random.randint(20, 80))
            meal_fat = meal.get('fat', np.random.randint(5, 30))
        else:
            meal_calories = np.random.randint(200, 600)
            meal_protein = np.random.randint(10, 50)
            meal_carbs = np.random.randint(20, 80)
            meal_fat = np.random.randint(5, 30)
        
        # Intensity and goal
        intensity = np.random.choice(intensities)
        goal = np.random.choice(goals)
        
        # Dietary preference match
        preference_match = np.random.choice([0, 1])
        
        # Calculate label (1 = good recommendation, 0 = bad)
        # Good if macros are within 80-120% of target
        cal_match = 0.8 <= (meal_calories / (target_calories / 4)) <= 1.2
        protein_match = 0.8 <= (meal_protein / (target_protein / 4)) <= 1.2
        
        label = 1 if (cal_match and protein_match and preference_match) else 0
        
        training_data.append({
            'target_calories': target_calories,
            'target_protein': target_protein,
            'target_carbs': target_carbs,
            'target_fat': target_fat,
            'meal_calories': meal_calories,
            'meal_protein': meal_protein,
            'meal_carbs': meal_carbs,
            'meal_fat': meal_fat,
            'intensity': intensity,
            'goal': goal,
            'preference_match': preference_match,
            'label': label
        })
    
    train_df = pd.DataFrame(training_data)
    print(f"✅ Created {len(train_df)} training samples")
    
    # Encode categorical variables
    print("\n🔢 Encoding categorical variables...")
    
    le_intensity = LabelEncoder()
    le_goal = LabelEncoder()
    
    train_df['intensity_encoded'] = le_intensity.fit_transform(train_df['intensity'])
    train_df['goal_encoded'] = le_goal.fit_transform(train_df['goal'])
    
    # Prepare features
    feature_columns = [
        'target_calories', 'target_protein', 'target_carbs', 'target_fat',
        'meal_calories', 'meal_protein', 'meal_carbs', 'meal_fat',
        'intensity_encoded', 'goal_encoded', 'preference_match'
    ]
    
    X = train_df[feature_columns]
    y = train_df['label']
    
    print(f"   Features: {X.shape}")
    print(f"   Labels: {y.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train XGBoost model
    print("\n🤖 Training XGBoost model...")
    
    model = xgb.XGBClassifier(
        max_depth=6,
        learning_rate=0.3,
        n_estimators=100,
        objective='binary:logistic',
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"   Training Accuracy: {train_score:.2%}")
    print(f"   Testing Accuracy: {test_score:.2%}")
    
    # Save model
    model_path = os.path.join(models_dir, 'xgb_meal.pkl')
    joblib.dump(model,   os.path.join(models_dir, 'xgb_meal.pkl'))
    # Save encoders
    le_goal_path = os.path.join(models_dir, 'le_goal.pkl')
    joblib.dump(le_goal, os.path.join(models_dir, 'le_goal.pkl'))
    print(f"\n✅ Model saved to: {model_path}")
    print(f"✅ Goal encoder saved to: {le_goal_path}")
    
    print("\n" + "=" * 60)
    print("✅ MEAL MODEL TRAINING COMPLETE!")
    print("=" * 60)
    print(f"\nFiles created:")
    print(f"  • {model_path}")
    print(f"  • {le_goal_path}")
    print(f"\nNext step: Start server with:")
    print(f"  python -m uvicorn app.main:app --reload --port 8000")

if __name__ == '__main__':
    train_meal_model()