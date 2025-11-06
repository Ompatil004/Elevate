import pandas as pd
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random
import google.generativeai as genai

# --- Constants ---
MODELS_DIR = "models"
DATA_DIR = "data"

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


class MealRequest(BaseModel):
    goal: str  # e.g., "Weight Loss", "Muscle Gain", "Maintain"
    calorie_target: int  # e.g., 500 (for a single meal)


# --- NEW Pydantic Models for Gemini ---
class ChatRequest(BaseModel):
    prompt: str


class MealItem(BaseModel):
    name: str
    calories: float
    protein: float
    fat: float
    carbohydrates: float  # ✅ Correct spelling for variable name


class CreativeMealRequest(BaseModel):
    goal: str
    meals: list[MealItem]


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
        return {"error": "Exercise data not loaded. Did you run train.py?"}

    try:
        target_body_part = map_workout_goal(request.goal)
        filtered_df = df_exercise[
            (df_exercise['difficulty'] == request.experience)
            & (df_exercise['bodyPart'] == target_body_part)
        ]

        if filtered_df.empty:
            filtered_df = df_exercise[df_exercise['difficulty'] == request.experience]

        if filtered_df.empty:
            return {"error": "No exercises found for this combination. Try 'Beginner'."}

        num_exercises = min(len(filtered_df), 5)
        recommendations = filtered_df.sample(num_exercises).to_dict('records')

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
        # ✅ Fixed column name ('carbohydrate' instead of 'carbohydrates')
        X_all = df_nutrition[['calories', 'protein', 'fat', 'carbohydrate']]

        predictions_encoded = meal_model.predict(X_all)
        predictions_str = meal_encoder.inverse_transform(predictions_encoded)

        df_pred = df_nutrition.copy()
        df_pred['predicted_goal'] = predictions_str

        goal_filtered_df = df_pred[df_pred['predicted_goal'] == request.goal]
        if goal_filtered_df.empty:
            return {"error": f"No food items found matching the goal '{request.goal}'."}

        calorie_tolerance = 75
        final_filtered_df = goal_filtered_df[
            (goal_filtered_df['calories'] > request.calorie_target - calorie_tolerance)
            & (goal_filtered_df['calories'] < request.calorie_target + calorie_tolerance)
        ]

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

    system_instruction = """
    You are 'Elevate', a friendly, encouraging, and knowledgeable AI health assistant
    for the 'Elevate' fitness platform. Your name is 'Elevate'.
    - Your responses must be concise, supportive, and focused ONLY on fitness,
      nutrition, health, and wellness.
    - If asked about any other topic (like politics, code, history, etc.),
      you must politely decline and steer the conversation back to health.
    - Keep answers to 2-3 short paragraphs maximum.
    """

    try:
        response = gemini_model.generate_content(
            request.prompt,
            generation_config={"temperature": 0.7},
            system_instruction=system_instruction
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
