from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MODELS =====
class UserProfile(BaseModel):
    username: str
    email: str
    age: int
    gender: str
    weight: float
    height: float
    goal: str
    experience: str
    equipment: List[str] = []
    body_issues: List[str] = []
    dietary_preference: str = "Non-Veg"
    allergies: List[str] = []

class WorkoutPlanRequest(BaseModel):
    goal: str
    experience: str
    equipment: List[str] = []
    body_issues: List[str] = []
    streak: Optional[int] = 0

class MealPlanRequest(BaseModel):
    age: int
    weight: float
    height: float
    gender: str
    goal: str
    dietary_preference: str = "Non-Veg"
    allergies: List[str] = []
    today_workout: Optional[Dict] = None

# ===== MISSING ENDPOINTS (ADD THESE) =====

@app.post("/api/users/save")
async def save_user_profile(profile: UserProfile):
    """Save user profile"""
    try:
        # TODO: Save to database (MongoDB)
        # For now, just return success
        print(f"📝 Saving user profile: {profile.username}")
        
        return {
            "success": True,
            "message": "User profile saved successfully",
            "data": profile.dict()
        }
    except Exception as e:
        print(f"❌ Error saving user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workout/save")
async def save_workout_plan(data: dict):
    """Save workout plan"""
    try:
        print(f"📝 Saving workout plan for user: {data.get('user_id', 'unknown')}")
        
        # TODO: Save to database
        
        return {
            "success": True,
            "message": "Workout plan saved successfully",
            "data": data
        }
    except Exception as e:
        print(f"❌ Error saving workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meals/save")
async def save_meal_plan(data: dict):
    """Save meal plan"""
    try:
        print(f"📝 Saving meal plan for user: {data.get('user_id', 'unknown')}")
        
        # TODO: Save to database
        
        return {
            "success": True,
            "message": "Meal plan saved successfully",
            "data": data
        }
    except Exception as e:
        print(f"❌ Error saving meals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/progress/save")
async def save_progress(data: dict):
    """Save user progress"""
    try:
        print(f"📝 Saving progress for user: {data.get('user_id', 'unknown')}")
        
        # TODO: Save to database
        
        return {
            "success": True,
            "message": "Progress saved successfully",
            "data": data
        }
    except Exception as e:
        print(f"❌ Error saving progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add these endpoints BEFORE the bottom of the file
@app.post("/generate-plan")
async def generate_plan(profile: dict):
    """Generate AI workout and meal plan"""
    try:
        print(f"🤖 Generating AI plan for user")

        return {
            "success": True,
            "message": "AI plan generated successfully",
            "workout_plan": {
                "plan_type": "Beginner Strength",
                "days_per_week": 3,
                "exercises": ["Push-ups", "Squats", "Lunges"]
            },
            "meal_plan": {
                "calories": 2000,
                "meals": ["Breakfast", "Lunch", "Dinner"]
            }
        }
    except Exception as e:
        print(f"❌ Error generating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/profile/update")
async def update_profile_endpoint(profile: UserProfile):
    """Update user profile"""
    try:
        print(f"📝 Updating user profile: {profile.username}")

        # In a real implementation, you would update the user profile in database
        # For now, just return success
        return {
            "success": True,
            "message": "User profile updated successfully",
            "data": profile.dict()
        }
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/profile/update-with-regeneration")
async def update_profile_and_regenerate(profile: UserProfile):
    """Update user profile and regenerate workout/meal plans if needed"""
    try:
        print(f"🔄 Updating profile and regenerating plans for: {profile.username}")

        # Debug: Print the received profile to see what's being received
        print(f"Received profile data: {profile.dict()}")

        # Determine if changes require plan regeneration
        changes_affect_workout = any([
            profile.experience != "intermediate",  # This would be compared to old profile
            profile.goal != "general_fitness",     # This would be compared to old profile
            len(profile.body_issues) > 0,          # This would be compared to old profile
            len(profile.equipment) > 0             # This would be compared to old profile
        ])

        changes_affect_meal = any([
            profile.goal != "general_fitness",      # This would be compared to old profile
            profile.dietary_preference != "Non-Veg", # This would be compared to old profile
            len(profile.allergies) > 0              # This would be compared to old profile
        ])

        print(f"Changes affecting workout: {changes_affect_workout}")
        print(f"Changes affecting meal: {changes_affect_meal}")

        response_data = {
            "success": True,
            "message": "Profile updated and plans regenerated successfully",
            "data": profile.dict(),
            "profile_changes": {
                "affect_workout_plans": changes_affect_workout,
                "affect_meal_plans": changes_affect_meal
            }
        }

        # Regenerate workout plan if needed
        if changes_affect_workout:
            print("Regenerating workout plan...")
            response_data["regenerated_workout"] = {
                "plan_type": f"{profile.experience.title()} {profile.goal.title()} Plan",
                "days_per_week": 3 if profile.experience == "beginner" else 4,
                "exercises": ["Custom exercises based on profile"],
                "equipment_needed": profile.equipment,
                "injuries_considered": profile.body_issues
            }

        # Regenerate meal plan if needed
        if changes_affect_meal:
            print("Regenerating meal plan...")
            response_data["regenerated_meal"] = {
                "calories": int(profile.weight * 25),  # Example calculation
                "dietary_restrictions": profile.allergies,
                "preference_aligned": profile.dietary_preference,
                "meals": ["Custom meals based on new preferences"]
            }

        print("Returning successful response")
        return response_data
    except Exception as e:
        print(f"❌ Error updating profile with regeneration: {e}")
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        raise HTTPException(status_code=500, detail=str(e))

# ===== EXISTING ENDPOINTS =====

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "elevate_fitness",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/ml/get-weekly-plan")
async def get_weekly_plan(request: WorkoutPlanRequest):
    """Generate weekly workout plan"""
    try:
        from app.workout_engine import get_workout_engine
        
        workout_engine = get_workout_engine()
        
        user_profile = {
            'goal': request.goal,
            'experience': request.experience,
            'equipment': request.equipment,
            'body_issues': request.body_issues,
            'streak': request.streak,
            'age': 25,
            'weight': 70,
            'height': 175
        }
        
        weekly_plan = workout_engine.generate_weekly_plan(user_profile)
        
        return {
            'success': True,
            'workout': weekly_plan,
            'message': f'Weekly plan generated for {request.goal} goal'
        }
    except Exception as e:
        print(f"❌ Error generating weekly plan: {e}")
        return {
            'success': False,
            'error': str(e),
            'workout': []
        }

@app.post("/ml/get-daily-meals")
async def get_daily_meals(request: MealPlanRequest):
    """Generate daily meal plan"""
    try:
        from app.meal_engine import get_meal_engine
        
        meal_engine = get_meal_engine()
        
        user_profile = {
            'age': request.age,
            'weight': request.weight,
            'height': request.height,
            'gender': request.gender,
            'goal': request.goal,
            'dietary_preference': request.dietary_preference,
            'allergies': request.allergies
        }
        
        meal_plan = meal_engine.suggest_daily_meals(
            user_profile,
            request.today_workout
        )
        
        return {
            'success': True,
            'meal_plan': meal_plan,
            'message': meal_plan.get('note', 'Meal plan generated')
        }
    except Exception as e:
        print(f"❌ Error generating meal plan: {e}")
        return {
            'success': False,
            'error': str(e),
            'meal_plan': {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'daily_target': {},
                'meals': []
            }
        }

# ===== STARTUP =====
@app.on_event("startup")
async def startup_event():
    print("FastAPI server started on port 8000")
    print("Loading exercise and nutrition data...")
    try:
        from app.workout_engine import get_workout_engine
        from app.meal_engine import get_meal_engine

        workout_engine = get_workout_engine()
        meal_engine = get_meal_engine()

        print("Data engines loaded successfully")
    except Exception as e:
        print(f"Warning: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    print("Server shutting down")