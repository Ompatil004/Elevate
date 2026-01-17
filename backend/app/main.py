from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import cv2
import pandas as pd
from app.ml_utils import ml_service
from app.pose_tracker import PoseTracker

app = FastAPI(title="Elevate AI API", version="1.0")

class ExerciseSelectRequest(BaseModel):
    exercise_name: str


# Enable CORS (Allows frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Schemas ---
class WorkoutRequest(BaseModel):
    goal: str 
    experience: str 

class MealRequest(BaseModel):
    goal: str 
    calorie_target: Optional[int] = None

# --- Global Tracker ---
tracker = PoseTracker()
camera = None 

# --- Endpoints ---

@app.get("/")
def home():
    return {"status": "Elevate AI System Operational"}

@app.post("/ml/recommend-workout")
def recommend_workout(request: WorkoutRequest):
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
def generate_frames():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Apply AI Pose Detection
        frame, _ = tracker.process_frame(frame)
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.post("/ml/set-exercise")
def set_exercise(request: ExerciseSelectRequest):
    # Update the global tracker settings
    tracker.set_exercise(request.exercise_name)
    return {"status": "success", "current_exercise": request.exercise_name}

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')