"""
Simple test to debug the profile update endpoint
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the same model as in main.py
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


@app.put("/profile/update-with-regeneration")
async def update_profile_and_regenerate_debug(profile: UserProfile):
    """Debug version of the profile update endpoint"""
    try:
        print(f"Received profile: {profile}")
        print(f"Username: {profile.username}")
        print(f"Goal: {profile.goal}")
        print(f"Experience: {profile.experience}")
        print(f"Equipment: {profile.equipment}")
        print(f"Body issues: {profile.body_issues}")
        print(f"Allergies: {profile.allergies}")
        
        # Simple response without complex logic
        response_data = {
            "success": True,
            "message": "Profile updated successfully",
            "data": profile.dict()
        }
        
        print("Returning response successfully")
        return response_data
    except Exception as e:
        print(f"Error in debug endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)