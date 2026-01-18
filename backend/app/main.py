from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.auth import router as auth_router
from app.history import router as history_router
from app.pose_tracker import PoseTracker
from app.ml_utils import ml_service
from pydantic import BaseModel
from typing import List
import cv2
import uvicorn
import time

<<<<<<< HEAD
app = FastAPI(
    title="Elevate AI API",
    version="1.0",
    description="AI-powered fitness and nutrition platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)
=======
app = FastAPI()
>>>>>>> 09ad0f416e64dcd001fe0eda2ba74a1ade4d507b

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(history_router, prefix="/history")

tracker = PoseTracker()

# --- GLOBAL KILL SWITCH ---
camera_active = False


<<<<<<< HEAD
@app.post("/ml/recommend-workout", summary="Get Workout Recommendations", description="Get personalized workout recommendations based on experience level")
def recommend_workout(request: WorkoutRequest):
    """
    Generate personalized workout recommendations.

    - **goal**: Fitness goal (Weight Loss, Muscle Gain, Maintain, Endurance, Strength)
    - **experience**: Experience level (Beginner, Intermediate, Advanced)

    Returns workout exercises tailored to the user's experience level.
    """
    print(f"Generating workout for: {request.experience}")
    exercises = ml_service.recommend_workout(request.experience)
    if not exercises:
        raise HTTPException(status_code=404, detail="No exercises found")
    return {"exercises": exercises}

@app.post("/ml/recommend-meal")
def recommend_meal(request: MealRequest):
    print(f"Generating meal plan for: {request.goal}")
    meals = ml_service.recommend_meals(request.goal, request.calorie_target)
    return {"recommendations": meals}

# --- Camera Streaming ---
=======
>>>>>>> 09ad0f416e64dcd001fe0eda2ba74a1ade4d507b
def generate_frames():
    global camera_active
    camera_active = True
    
    # ❌ OLD SLOW LINE: cap = cv2.VideoCapture(0)
    
    # ✅ NEW FAST LINE (Forces DirectShow on Windows):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
    
    # If CAP_DSHOW fails on Mac/Linux, fallback to standard:
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Camera is locked or unavailable.")
        return

    print("📷 Camera Started (Fast Mode).")
    
    try:
        while camera_active:
            success, frame = cap.read()
            if not success:
                break
            
            annotated_frame, _ = tracker.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret: continue
            
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Removed sleep or kept minimal
            time.sleep(0.01) 

    except Exception as e:
        print(f"⚠ Stream Error: {e}")

    finally:
        print("🛑 Closing Camera...")
        cap.release()
        cv2.destroyAllWindows()

# ... (Rest of the file remains the same) ...

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# --- NEW ENDPOINT: FORCE STOP ---
@app.post("/stop_camera")
def stop_camera():
    global camera_active
    print("🔻 Force Stop Requested by Frontend")
    camera_active = False # The generator loop will break on next iteration
    return {"status": "Camera stopping..."}

# --- DATA MODELS & OTHER ENDPOINTS ---
class ProfileData(BaseModel):
    user_id: str = "guest"
    experience: str
    goal: str
    age: int
    weight: float
    height: float
    gender: str
    equipment: List[str] = [] 
    allergies: List[str] = []
    dietary_preference: str = "Non-Veg"

class ExerciseSelectRequest(BaseModel):
    exercise_name: str

@app.post("/ml/get-daily-plan")
def get_daily_plan(profile: ProfileData):
    workout_plan = ml_service.recommend_workout(
        user_profile={"age": profile.age, "weight": profile.weight, "height": profile.height, "gender": profile.gender, "goal": profile.goal},
        available_equipment=profile.equipment
    )
    meal_plan = ml_service.recommend_meals(
        goal=profile.goal,
        diet_preference=profile.dietary_preference,
        allergies=profile.allergies
    )
    return {"workout": workout_plan, "nutrition": meal_plan}

@app.post("/ml/set-exercise")
def set_exercise(request: ExerciseSelectRequest):
    tracker.set_exercise(request.exercise_name)
    return {"status": "success"}

@app.get("/ml/workout-status")
def get_workout_status():
    return tracker.get_status()


# ... inside main.py ...

class SwapRequest(BaseModel):
    current_meal_name: str
    calories: int
    goal: str = "Maintenance"

@app.post("/ml/get-alternative-meal")
def get_alternative_meal(req: SwapRequest):
    print(f"🔄 Swapping meal: {req.current_meal_name}")
    try:
        # Ask ML Service for a similar food
        new_meal = ml_service.get_similar_food(req.current_meal_name, req.calories)
        return new_meal
    except Exception as e:
        print(f"Swap Error: {e}")
        return {"name": "Protein Shake & Banana", "calories": 250, "protein": 25, "quantity": "1 Serving"}