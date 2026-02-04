from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime
import os
import sys
import logging

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.workout_engine import get_workout_engine
from app.meal_engine import get_meal_engine

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Elevate Fitness API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines on startup
workout_engine = None
meal_engine = None

@app.on_event("startup")
async def startup_event():
    global workout_engine, meal_engine
    print("\n" + "="*60)
    print("FastAPI Server Starting...")
    print("="*60)

    # Connect to MongoDB (optional - continue if it fails)
    from app.db import connect_to_mongo
    try:
        await connect_to_mongo()
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        print("⚠️ Continuing without MongoDB - workout/nutrition APIs will still work")
        # Don't raise - continue startup

    try:
        workout_engine = get_workout_engine()
        print("WorkoutEngine initialized successfully")
    except Exception as e:
        print(f"WorkoutEngine error: {e}")
        import traceback
        traceback.print_exc()

    try:
        meal_engine = get_meal_engine()
        print("MealEngine initialized successfully")
    except Exception as e:
        print(f"MealEngine error: {e}")
        import traceback
        traceback.print_exc()

    print("="*60)
    print("Server ready at http://localhost:8000")
    print("="*60 + "\n")

# ==========================================
# HEALTH & STATUS
# ==========================================

@app.get("/")
async def root():
    return {
        "message": "🏋️ Elevate Fitness API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "elevate_fitness",
        "timestamp": datetime.utcnow().isoformat(),
        "engines": {
            "workout": workout_engine is not None,
            "meal": meal_engine is not None
        }                                              
    }

# ==========================================
# WORKOUT ENDPOINT
# ==========================================

@app.post("/workout")
async def generate_workout(profile: dict):
    """Generate workout plan using local ML engine"""
    try:
        print(f"\n{'='*60}")
        print(f"📋 WORKOUT REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"Received profile: {profile}")

        if workout_engine is None:
            print("❌ ERROR: WorkoutEngine is None!")
            raise HTTPException(status_code=500, detail="WorkoutEngine not initialized")

        # Safely extract fields with defaults
        user_data = {
            'goal': profile.get('goal', 'Muscle Gain'),
            'experience': profile.get('experience', 'Beginner'),
            'days_per_week': profile.get('days_per_week', 4),
            'equipment': profile.get('equipment', ['Dumbbell']),
            'body_issues': profile.get('body_issues', []),
            'streak': profile.get('streak', 0)
        }

        print(f"Processed user data: {user_data}")
        print(f"Generating {user_data['days_per_week']}-day workout...")

        # Generate workout
        weekly_plan = workout_engine.generate_weekly_plan(user_data)

        if not weekly_plan or len(weekly_plan) == 0:
            print("ERROR: Generated plan is empty!")
            raise HTTPException(status_code=500, detail="Generated empty workout plan")

        total_exercises = sum(len(day.get('exercises', [])) for day in weekly_plan)
        print(f"SUCCESS: Generated {len(weekly_plan)} days with {total_exercises} total exercises")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "workout": weekly_plan,
            "exercises_count": total_exercises
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ CRITICAL ERROR in /workout endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback
        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )

# ==========================================
# NUTRITION ENDPOINT
# ==========================================

@app.post("/nutrition")
async def generate_nutrition(profile: dict):
    """Generate nutrition plan using local ML engine"""
    try:
        print(f"\n🍽️ Nutrition request received")
        print(f"   Profile: {profile}")

        if meal_engine is None:
            raise Exception("MealEngine not initialized")

        # Prepare user profile with defaults
        user_profile = {
            'age': profile.get('age', 25),
            'weight': profile.get('weight', 70),
            'height': profile.get('height', 175),
            'gender': profile.get('gender', 'Male'),
            'goal': profile.get('goal', 'Muscle Gain'),
            'dietary_preference': profile.get('dietary_preference', 'Non-Veg'),
            'allergies': profile.get('allergies', [])
        }

        print(f"🍽️ Generating nutrition for {user_profile['goal']}")

        # Generate using engine
        meal_plan = meal_engine.suggest_daily_meals(user_profile)

        print(f"✅ Generated {len(meal_plan.get('meals', []))} meals\n")

        return {
            "success": True,
            "nutrition": meal_plan,
            "ml_powered": True,
            "source": "MealEngine",
            "meals_count": len(meal_plan.get('meals', [])),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"❌ Nutrition error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ==========================================
# PROFILE UPDATE ENDPOINT
# ==========================================

@app.put("/profile/update")
async def update_profile(profile_update: dict):
    """Update user profile and regenerate workouts based on new parameters"""
    try:
        print(f"\n{'='*60}")
        print(f"🔄 PROFILE UPDATE REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"Profile update data: {profile_update}")

        if workout_engine is None:
            print("❌ ERROR: WorkoutEngine is None!")
            raise HTTPException(status_code=500, detail="WorkoutEngine not initialized")

        # Extract user ID and updated profile fields
        user_id = profile_update.get('user_id')
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        # Get the collections
        from app.db import get_user_collection, get_workout_history_collection, get_workout_completion_collection
        user_collection = get_user_collection()
        workout_history_collection = get_workout_history_collection()
        workout_completion_collection = get_workout_completion_collection()

        # Find the existing user
        user_doc = await user_collection.find_one({"id": user_id})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user profile with new values
        update_fields = {}
        profile_fields = ['goal', 'experience', 'weight', 'age', 'height', 'gender', 'equipment', 'body_issues', 'days_per_week', 'dietary_preference', 'allergies']

        for field in profile_fields:
            if field in profile_update:
                update_fields[field] = profile_update[field]

        # Update the user document
        await user_collection.update_one(
            {"id": user_id},
            {"$set": {**update_fields, "updated_at": datetime.utcnow()}}
        )

        # Get the updated user profile
        updated_user = await user_collection.find_one({"id": user_id})

        # Prepare user data for workout generation
        user_data = {
            'goal': updated_user.get('goal', 'Muscle Gain'),
            'experience': updated_user.get('experience', 'Beginner'),
            'days_per_week': updated_user.get('days_per_week', 4),
            'equipment': updated_user.get('equipment', []),
            'body_issues': updated_user.get('body_issues', []),
            'streak': updated_user.get('streak', 0),
            'weight': updated_user.get('weight', 70),
            'age': updated_user.get('age', 25),
            'height': updated_user.get('height', 175),
            'consistency': updated_user.get('consistency', 0.7)
        }

        print(f"Regenerating workout with updated profile: {user_data}")

        from datetime import date, timedelta

        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # Check if today's workout is completed
        today_completion = await workout_completion_collection.find_one({
            "user_id": user_id,
            "date": {"$gte": today_start, "$lt": today_end}
        })

        # Determine regeneration start date
        if today_completion and today_completion.get('completed', False):
            print("✅ Today's workout is completed, starting regeneration from tomorrow")
            start_date = today + timedelta(days=1)
        else:
            print("📋 Today's workout is NOT completed, regenerating from today")
            start_date = today

        # Generate new 7-day weekly plan
        new_weekly_plan = workout_engine.generate_weekly_plan(user_data)

        if not new_weekly_plan or len(new_weekly_plan) != 7:
            raise HTTPException(status_code=500, detail="Generated plan must have 7 days")

        # Delete all future workout records (from start_date onwards)
        delete_result = await workout_history_collection.delete_many({
            "user_id": user_id,
            "date": {"$gte": datetime.combine(start_date, datetime.min.time())}
        })

        print(f"🗑️ Deleted {delete_result.deleted_count} future/incomplete workout records")

        # Insert new workout records for the next 7 days starting from start_date
        regenerated_count = 0
        for i in range(7):
            target_date = start_date + timedelta(days=i)
            day_of_week = target_date.weekday()  # Monday=0, Sunday=6

            # Find the matching day in the weekly plan
            day_workout = None
            for day_plan in new_weekly_plan:
                if day_plan.get('day_of_week') == day_of_week:
                    day_workout = day_plan
                    break

            # Fallback to index if day_of_week not found
            if day_workout is None and len(new_weekly_plan) > day_of_week:
                day_workout = new_weekly_plan[day_of_week]

            if day_workout:
                workout_record = {
                    "user_id": user_id,
                    "date": datetime.combine(target_date, datetime.min.time()),
                    "workout_plan": [day_workout],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }

                await workout_history_collection.insert_one(workout_record)
                regenerated_count += 1

        # Store the new weekly plan in user profile
        await user_collection.update_one(
            {"id": user_id},
            {"$set": {
                "current_weekly_plan": new_weekly_plan,
                "plan_generated_at": datetime.utcnow()
            }}
        )

        print(f"✅ SUCCESS: Profile updated and {regenerated_count} workouts regenerated for user {user_id}")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "message": f"Profile updated successfully and {regenerated_count} workouts regenerated",
            "updated_fields": list(update_fields.keys()),
            "regenerated_workouts": regenerated_count,
            "regeneration_start_date": start_date.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ CRITICAL ERROR in /profile/update endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback
        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )


# ==========================================
# ERROR HANDLER
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )