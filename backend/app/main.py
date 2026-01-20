from fastapi import FastAPI
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

app = FastAPI()

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
camera_active = False

def generate_frames():
    global camera_active
    camera_active = True
    
    # FAST STARTUP FOR WINDOWS
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened(): cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Camera Error")
        return

    try:
        while camera_active:
            success, frame = cap.read()
            if not success: break
            
            annotated_frame, _ = tracker.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret: continue
            
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.01)

    except Exception: pass
    finally:
        cap.release()
        cv2.destroyAllWindows()

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/stop_camera")
def stop_camera():
    global camera_active
    camera_active = False
    return {"status": "Stopped"}

# --- MEAL SWAP & ML ENDPOINTS ---
class SwapRequest(BaseModel):
    current_meal_name: str
    calories: int
    goal: str = "Maintenance"

@app.post("/ml/get-alternative-meal")
def get_alternative_meal(req: SwapRequest):
    try:
        return ml_service.get_similar_food(req.current_meal_name, req.calories)
    except:
        return {"name": "Banana Shake", "calories": 250, "protein": 5, "quantity": "1 Serving"}

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

@app.post("/ml/get-daily-plan")
def get_daily_plan(profile: ProfileData):
    w = ml_service.recommend_workout(
        {"age": profile.age, "weight": profile.weight, "height": profile.height, "gender": profile.gender, "goal": profile.goal},
        profile.equipment
    )
    m = ml_service.recommend_meals(profile.goal, profile.dietary_preference, profile.allergies)
    return {"workout": w, "nutrition": m}

class ExerciseSelectRequest(BaseModel):
    exercise_name: str

@app.post("/ml/set-exercise")
def set_exercise(req: ExerciseSelectRequest):
    tracker.set_exercise(req.exercise_name)
    return {"status": "ok"}

@app.get("/ml/workout-status")
def get_workout_status():
    return tracker.get_status()