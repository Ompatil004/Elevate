"""
Simple test to verify the endpoint works with correct field names
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
    body_issues: List[str] = []  # This is the correct field name
    dietary_preference: str = "Non-Veg"
    allergies: List[str] = []


@app.put("/profile/update-with-regeneration")
async def simple_test_endpoint(profile: UserProfile):
    """Simple test endpoint to verify basic functionality"""
    try:
        print(f"Received profile: {profile.username}")
        print(f"Body issues: {profile.body_issues}")
        print(f"Equipment: {profile.equipment}")
        print(f"Allergies: {profile.allergies}")
        
        # Return simple response
        return {
            "success": True,
            "message": "Profile received successfully",
            "received_data": profile.dict()
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Test route to verify server is running
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "debug_test"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")