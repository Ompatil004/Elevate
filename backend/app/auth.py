from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
import motor.motor_asyncio
from bson import ObjectId # Import ObjectId to find user by ID

router = APIRouter()

# Database Setup
MONGO_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.elevate_ai_db
users_collection = db.users

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- DATA MODELS ---
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

# --- NEW: Model for Profile Update ---
class UserProfileUpdate(BaseModel):
    user_id: str
    age: int
    weight: float
    height: float
    gender: str
    goal: str
    experience: str
    equipment: List[str] = []
    allergies: List[str] = []
    dietary_preference: str

# --- HELPER FUNCTIONS ---
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- ENDPOINTS ---

@router.post("/register", status_code=201)
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)

    user_doc = {
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        # Initialize empty profile fields
        "age": None, "weight": None, "height": None, "goal": None
    }
    await users_collection.insert_one(user_doc)
    
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {
        "message": "Login successful", 
        "user_id": str(db_user["_id"]),
        "full_name": db_user["full_name"]
    }

# --- NEW: Endpoint to Save Profile ---
@router.post("/update-profile")
async def update_profile(data: UserProfileUpdate):
    try:
        # Convert string ID to MongoDB ObjectId
        obj_id = ObjectId(data.user_id)
        
        # Update the user document
        result = await users_collection.update_one(
            {"_id": obj_id},
            {"$set": {
                "age": data.age,
                "weight": data.weight,
                "height": data.height,
                "gender": data.gender,
                "goal": data.goal,
                "experience": data.experience,
                "equipment": data.equipment,
                "allergies": data.allergies,
                "dietary_preference": data.dietary_preference,
                "is_profile_complete": True
            }}
        )
        
        if result.modified_count == 0:
            # If user wasn't found (rare)
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "Profile updated successfully"}

    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # ... (Keep existing imports and code)

# --- NEW: Get Profile Endpoint ---
@router.get("/get-profile/{user_id}")
async def get_profile(user_id: str):
    try:
        if not user_id or user_id == "null":
            raise HTTPException(status_code=400, detail="Invalid User ID")

        obj_id = ObjectId(user_id)
        user = await users_collection.find_one({"_id": obj_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Check if they have actually set up their profile (look for 'age')
        if not user.get("age"):
            return {"is_setup": False}
            
        # Return the profile data
        return {
            "is_setup": True,
            "user_id": str(user["_id"]),
            "age": user.get("age"),
            "weight": user.get("weight"),
            "height": user.get("height"),
            "gender": user.get("gender"),
            "goal": user.get("goal"),
            "experience": user.get("experience"),
            "equipment": user.get("equipment", []),
            "allergies": user.get("allergies", []),
            "dietary_preference": user.get("dietary_preference", "Both")
        }

    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))