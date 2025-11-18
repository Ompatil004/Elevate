import pandas as pd
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random
import google.generativeai as genai

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# --- Constants ---
MODELS_DIR = "ml/models"
DATA_DIR = "ml/data"

# Load data and models at startup
try:
    # Load processed data
    df_nutrition = pd.read_csv(os.path.join(DATA_DIR, "nutrition_processed.csv"))
    df_exercise = pd.read_csv(os.path.join(DATA_DIR, "fitness_exercises_processed.csv"))

    # Load meal model
    meal_model = joblib.load(os.path.join(MODELS_DIR, "meal_model.joblib"))
    meal_encoder = joblib.load(os.path.join(MODELS_DIR, "meal_encoder.joblib"))

    # Load workout model (Though we might use logic-based filtering)
    workout_model = joblib.load(os.path.join(MODELS_DIR, "workout_model.joblib"))
    workout_encoders = joblib.load(os.path.join(MODELS_DIR, "workout_encoders.joblib"))

    print("Data and models loaded successfully.")
except FileNotFoundError:
    print("=" * 50)
    print("ERROR: Model or data files not found.")
    print("Please run `python train.py` first to create the necessary files.")
    print("=" * 50)
    # We don't exit, but the API will fail if files are missing
    df_nutrition, df_exercise = None, None
except Exception as e:
    print(f"Error loading models or data: {e}")
    df_nutrition, df_exercise = None, None

# --- Gemini API Setup ---
try:
    GEMINI_API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    print("Gemini API configured successfully.")
except KeyError:
    print("=" * 50)
    print("ERROR: GOOGLE_API_KEY environment variable not set.")
    print("Please set the environment variable to use Gemini features.")
    print("=" * 50)
    gemini_model = None
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    gemini_model = None


# --- API Setup ---
app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models (Request Bodies) ---
class WorkoutRequest(BaseModel):
    goal: str  # e.g., "Strength", "Cardio"
    experience: str  # e.g., "Beginner", "Intermediate", "Advanced"

    # NEW ATTRIBUTES:
    equipment_available: list[str] = []  # ["Dumbbells", "Barbell", "Resistance Bands", "Gym", "Bodyweight Only"]
    time_available: int = None  # Available time in minutes
    target_muscle_group: str = None  # "Chest", "Back", "Legs", "Arms", "Core", "Full Body"
    injury_history: list[str] = []  # ["Knee", "Shoulder", "Back", "Elbow"] - to avoid certain movements
    preferred_exercise_type: str = None  # "Free Weights", "Machines", "Bodyweight", "Cardio"
    intensity_level: str = None  # "Low", "Moderate", "High", "Extreme"
    frequency_per_week: int = None  # How many days per week
    focus_area: str = None  # "Strength", "Hypertrophy", "Endurance", "Fat Loss"
    gym_or_home: str = None  # "Gym", "Home", "Outdoor", "Any"
    specific_body_part: str = None  # More specific targeting than goal
    cardio_minutes: int = None  # If cardio is part of the routine
    rest_days: list[str] = []  # Days when user doesn't want to workout (["Monday", "Thursday"])
    progression_type: str = None  # "Linear", "Pyramid", "Drop Sets", "Supersets"


class MealRequest(BaseModel):
    goal: str  # e.g., "Weight Loss", "Muscle Gain", "Maintain"
    calorie_target: int  # e.g., 500 (for a single meal)

    # NEW ATTRIBUTES:
    meal_type: str = None  # "Breakfast", "Lunch", "Dinner", "Snack"
    dietary_restrictions: list[str] = []  # ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free"]
    allergies: list[str] = []  # ["Nuts", "Shellfish", "Soy", "Wheat"]
    meal_time: str = None  # "Quick" (under 15 mins), "Moderate" (15-30 mins), "Extended" (30+ mins)
    budget: float = None  # Max cost per meal
    protein_target: float = None  # Target protein in grams
    carb_target: float = None  # Target carbs in grams
    fat_target: float = None  # Target fat in grams
    preferred_cuisine: str = None  # "Italian", "Asian", "Mexican", "American"
    cooking_skill: str = None  # "Beginner", "Intermediate", "Advanced"
    ingredients: list[str] = []  # Specific ingredients to include
    avoid_ingredients: list[str] = []  # Ingredients to avoid
    spice_level: int = None  # 1-5 scale for spiciness
    prep_time: int = None  # Maximum prep time in minutes


# --- NEW Pydantic Models for Gemini ---
class ChatRequest(BaseModel):
    prompt: str

    # NEW ATTRIBUTES:
    user_profile: dict = None  # {"age": int, "gender": str, "height": int, "weight": int, "fitness_level": str, "medical_conditions": list}
    context: str = None  # "Workout", "Nutrition", "Recovery", "General"
    response_length: str = None  # "Brief", "Moderate", "Detailed"


class MealItem(BaseModel):
    name: str
    calories: float
    protein: float
    fat: float
    carbohydrates: float  # ✅ Correct spelling for variable name


class CreativeMealRequest(BaseModel):
    goal: str
    meals: list[MealItem]


# --- Pydantic Models for Computer Vision ---
class ExerciseTrackingRequest(BaseModel):
    exercise_name: str
    camera_index: int = 0


# --- Helper Functions ---
def map_workout_goal(goal: str):
    """Maps a general goal to a specific bodyPart from the dataset."""
    goal_map = {
        "Strength": ["chest", "back", "upper legs", "shoulders"],
        "Cardio": ["cardio"],
        "Muscle Gain": ["upper arms", "lower arms", "upper legs", "shoulders", "chest", "back"]
    }
    # Return a random body part from the list for variety
    selected_parts = goal_map.get(goal, ["chest", "back", "upper legs"])  # Default
    return random.choice(selected_parts)


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Elevate AI-ML API is running!"}


@app.post("/ml/recommend-workout")
def recommend_workout(request: WorkoutRequest):
    """Recommends a workout plan using logic-based filtering."""
    if df_exercise is None:
        return {"error": "Exercise data or model not loaded. Did you run train.py?"}

    try:
        # Start with body part mapping based on goal
        target_body_part = map_workout_goal(request.goal)

        # Filter by difficulty and body part first
        filtered_df = df_exercise[
            (df_exercise['difficulty'] == request.experience)
            & (df_exercise['bodyPart'] == target_body_part)
        ]

        # Apply additional filters based on new attributes if provided
        final_df = filtered_df.copy()

        # Filter by equipment available if provided
        if request.equipment_available:
            # The equipment column in the dataset uses specific values, so we need to match them
            valid_equipment = []
            for equip in request.equipment_available:
                # Map the user-friendly equipment names to the ones in the dataset
                if equip.lower() in ['dumbbells', 'dumbbell']:
                    valid_equipment.append('dumbbell')
                elif equip.lower() in ['barbell', 'barbell']:
                    valid_equipment.append('barbell')
                elif equip.lower() in ['resistance bands', 'resistance band', 'band']:
                    valid_equipment.append('resistance band')
                elif equip.lower() in ['gym']:
                    # For gym, include equipment that typically requires gym access
                    valid_equipment.extend(['cable', 'smith machine', 'machine'])
                elif equip.lower() in ['bodyweight only', 'body weight', 'bodyweight']:
                    valid_equipment.append('body weight')

            # Filter exercises based on equipment
            if valid_equipment:
                final_df = final_df[final_df['equipment'].isin(valid_equipment)]

        # Filter by target muscle group if provided
        if request.target_muscle_group:
            final_df = final_df[final_df['bodyPart'] == request.target_muscle_group.lower()]

        # Filter by preferred exercise type if provided
        if request.preferred_exercise_type:
            if request.preferred_exercise_type.lower() in ['free weights', 'free weight']:
                free_weight_equipment = ['dumbbell', 'barbell', 'ez barbell', 'olympic barbell']
                final_df = final_df[final_df['equipment'].isin(free_weight_equipment)]
            elif request.preferred_exercise_type.lower() in ['machines', 'machine']:
                final_df = final_df[final_df['equipment'] == 'machine']
            elif request.preferred_exercise_type.lower() in ['bodyweight', 'body weight', 'bodyweight only']:
                final_df = final_df[final_df['equipment'] == 'body weight']
            elif request.preferred_exercise_type.lower() in ['cardio']:
                final_df = final_df[final_df['bodyPart'] == 'cardio']

        # Filter by injury history to avoid exercises that target problematic areas
        if request.injury_history:
            # Map injury types to body parts to avoid
            injury_body_parts = []
            for injury in request.injury_history:
                injury_lower = injury.lower()
                if 'knee' in injury_lower:
                    injury_body_parts.extend(['lower legs', 'upper legs'])
                elif 'shoulder' in injury_lower:
                    injury_body_parts.extend(['shoulders', 'upper arms', 'chest', 'back'])
                elif 'back' in injury_lower:
                    injury_body_parts.extend(['back', 'waist'])
                elif 'elbow' in injury_lower:
                    injury_body_parts.extend(['upper arms', 'lower arms'])

            if injury_body_parts:
                final_df = final_df[~final_df['bodyPart'].isin(injury_body_parts)]

        # Filter by specific body part if provided (overrides goal-based mapping)
        if request.specific_body_part:
            final_df = final_df[final_df['bodyPart'] == request.specific_body_part.lower()]

        # If no results after all filters, fall back to initial filtered results
        if final_df.empty:
            final_df = filtered_df

        # If still empty, fall back to just experience level
        if final_df.empty:
            final_df = df_exercise[df_exercise['difficulty'] == request.experience]

        if final_df.empty:
            return {"error": "No exercises found for this combination. Try 'Beginner'."}

        num_exercises = min(len(final_df), 5)
        recommendations = final_df.sample(num_exercises).to_dict('records')

        return {
            "title": f"{request.experience} {target_body_part.title()} Workout",
            "exercises": recommendations
        }
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


@app.post("/ml/recommend-meal")
def recommend_meal(request: MealRequest):
    """Recommends meals using the trained XGBoost ML model."""
    if df_nutrition is None or meal_model is None:
        return {"error": "Nutrition data or model not loaded. Did you run train.py?"}

    try:

        X_all = df_nutrition[['calories', 'protein', 'fat', 'carbohydrate']]

        predictions_encoded = meal_model.predict(X_all)
        predictions_str = meal_encoder.inverse_transform(predictions_encoded)

        df_pred = df_nutrition.copy()
        df_pred['predicted_goal'] = predictions_str

        # Apply goal filter first
        goal_filtered_df = df_pred[df_pred['predicted_goal'] == request.goal]
        if goal_filtered_df.empty:
            return {"error": f"No food items found matching the goal '{request.goal}'."}

        # Apply calorie filter
        calorie_tolerance = 75
        calorie_filtered_df = goal_filtered_df[
            (goal_filtered_df['calories'] > request.calorie_target - calorie_tolerance)
            & (goal_filtered_df['calories'] < request.calorie_target + calorie_tolerance)
        ]

        # Apply additional filters based on new attributes if provided
        final_filtered_df = calorie_filtered_df.copy()

        # Filter by meal type if provided (assuming we'll add this to nutrition data in the training script)
        if request.meal_type:
            # For now, if data doesn't have this column, we skip this filter
            if 'meal_type' in final_filtered_df.columns:
                final_filtered_df = final_filtered_df[final_filtered_df['meal_type'] == request.meal_type]

        # Filter by dietary restrictions if provided
        if request.dietary_restrictions:
            # Assuming we'll add dietary restriction columns in the training script
            if 'dietary_restrictions' in final_filtered_df.columns:
                # This would require specific data processing in the training script
                pass

        # Filter by allergies if provided
        if request.allergies:
            # Assuming we'll add allergy information in the training script
            if 'allergens' in final_filtered_df.columns:
                # This would require specific data processing in the training script
                pass

        # Filter by protein target if provided
        if request.protein_target:
            protein_tolerance = request.protein_target * 0.2  # 20% tolerance
            final_filtered_df = final_filtered_df[
                (final_filtered_df['protein'] >= request.protein_target - protein_tolerance)
                & (final_filtered_df['protein'] <= request.protein_target + protein_tolerance)
            ]

        # Filter by carb target if provided
        if request.carb_target:
            carb_tolerance = request.carb_target * 0.2  # 20% tolerance
            final_filtered_df = final_filtered_df[
                (final_filtered_df['carbohydrate'] >= request.carb_target - carb_tolerance)
                & (final_filtered_df['carbohydrate'] <= request.carb_target + carb_tolerance)
            ]

        # Filter by fat target if provided
        if request.fat_target:
            fat_tolerance = request.fat_target * 0.2  # 20% tolerance
            final_filtered_df = final_filtered_df[
                (final_filtered_df['fat'] >= request.fat_target - fat_tolerance)
                & (final_filtered_df['fat'] <= request.fat_target + fat_tolerance)
            ]

        # If no results after all filters, fall back to calorie-filtered results
        if final_filtered_df.empty:
            final_filtered_df = calorie_filtered_df

        # If still empty, fall back to goal-filtered results
        if final_filtered_df.empty:
            final_filtered_df = goal_filtered_df

        num_meals = min(len(final_filtered_df), 3)
        recommendations = final_filtered_df.sample(num_meals).to_dict('records')

        return {
            "title": f"Meal Ideas for {request.goal} (around {request.calorie_target} kcal)",
            "meals": recommendations
        }
    except ValueError:
        return {"error": f"Invalid goal: '{request.goal}'. Valid goals are: {list(meal_encoder.classes_)}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


# --- NEW Gemini-Powered Endpoints ---
@app.post("/ml/chat")
async def chat(request: ChatRequest):
    """AI Health Assistant Chatbot powered by Gemini."""
    if gemini_model is None:
        return {"error": "Gemini API is not configured. Please set GOOGLE_API_KEY."}

    system_context = """
    You are 'Elevate', a friendly, encouraging, and knowledgeable AI health assistant
    for the 'Elevate' fitness platform. Your name is 'Elevate'.
    - Your responses must be concise, supportive, and focused ONLY on fitness,
      nutrition, health, and wellness.
    - If asked about any other topic (like politics, code, history, etc.),
      you must politely decline and steer the conversation back to health.
    - Keep answers to 2-3 short paragraphs maximum.
    """

    # Add user profile information to the context if available
    profile_context = ""
    if request.user_profile:
        profile_context = f"\nUser Profile: "
        if 'age' in request.user_profile:
            profile_context += f"Age: {request.user_profile['age']}, "
        if 'gender' in request.user_profile:
            profile_context += f"Gender: {request.user_profile['gender']}, "
        if 'height' in request.user_profile:
            profile_context += f"Height: {request.user_profile['height']}cm, "
        if 'weight' in request.user_profile:
            profile_context += f"Weight: {request.user_profile['weight']}kg, "
        if 'fitness_level' in request.user_profile:
            profile_context += f"Fitness Level: {request.user_profile['fitness_level']}, "
        if 'medical_conditions' in request.user_profile and request.user_profile['medical_conditions']:
            profile_context += f"Medical Conditions: {', '.join(request.user_profile['medical_conditions'])}. "

    # Add context information if provided
    context_info = ""
    if request.context:
        context_info = f"\nContext: The user is asking about {request.context.lower()}. "

    # Adjust the response length based on the request
    response_guidance = ""
    if request.response_length == "Brief":
        response_guidance = "Keep your response concise and to the point."
    elif request.response_length == "Detailed":
        response_guidance = "Provide a thorough and detailed response with actionable advice."
    else:  # Default or "Moderate"
        response_guidance = "Provide a balanced response with key points."

    prompt_with_context = f"{system_context}{profile_context}{context_info}{response_guidance}\n\nUser: {request.prompt}\n\nAssistant:"

    try:
        response = gemini_model.generate_content(
            prompt_with_context,
            generation_config={"temperature": 0.7}
        )
        return {"response": response.text}
    except Exception as e:
        return {"error": f"Error generating response from Gemini: {e}"}


@app.post("/ml/generate-meal-plan-creative")
async def generate_meal_plan_creative(request: CreativeMealRequest):
    """Uses Gemini to create a creative, simple 1-day meal plan."""
    if gemini_model is None:
        return {"error": "Gemini API is not configured. Please set GOOGLE_API_KEY."}

    meal_list = "\n".join(
        [f"- {meal.name} (Protein: {meal.protein}g, Cals: {int(meal.calories)})" for meal in request.meals]
    )

    prompt = f"""
    You are a creative and practical health chef.
    My goal is: "{request.goal}".
    My app's ML model suggested these food items:
    {meal_list}

    Turn these items into a simple, attractive 1-day meal plan (Breakfast, Lunch, Dinner).
    For each meal, give it a catchy name and a 1-2 sentence description of
    how to prepare it. Be creative and make it sound delicious.

    Example format:
    **Breakfast: Sunrise Protein Boost**
    A quick scramble of...

    **Lunch: Quick Muscle-Up Bowl**
    Toss the...

    **Dinner: Lean & Clean Plate**
    Simply pan-sear the...
    """

    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={"temperature": 0.8},
        )
        text_response = response.text.replace('\n', '<br>').replace('**', '<strong>')
        return {"response": text_response}
    except Exception as e:
        return {"error": f"Error generating response from Gemini: {e}"}


# --- Computer Vision Endpoints ---
@app.post("/ml/start-exercise-tracking")
async def start_exercise_tracking(request: ExerciseTrackingRequest):
    """Start computer vision tracking for a specific exercise."""
    try:
        # Import the exercise_cv module
        from exercise_cv import track_exercise_from_planner

        # This would start the exercise tracking in a separate thread/process
        # For now, return a message indicating the tracking is starting
        return {
            "message": f"Starting tracking for exercise: {request.exercise_name}",
            "exercise": request.exercise_name,
            "camera_index": request.camera_index
        }
    except Exception as e:
        return {"error": f"An error occurred during exercise tracking setup: {e}"}


@app.get("/ml/get-supported-exercises")
async def get_supported_exercises():
    """Get list of exercises supported by the computer vision module."""
    try:
        from exercise_cv import ExerciseRepCounter
        counter = ExerciseRepCounter()

        supported_exercises = list(counter.exercise_landmarks.keys())
        return {
            "supported_exercises": supported_exercises,
            "message": f"Currently supporting {len(supported_exercises)} exercises for rep counting"
        }
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


