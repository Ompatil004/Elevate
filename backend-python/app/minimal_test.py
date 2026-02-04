"""
Minimal working example to test the endpoint
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

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
async def test_endpoint(profile: UserProfile):
    """Test endpoint"""
    return {
        "success": True,
        "message": "Profile received successfully",
        "data": profile.dict()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)