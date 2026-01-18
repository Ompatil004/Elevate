from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional  # <--- Import Optional
import motor.motor_asyncio
from datetime import datetime

router = APIRouter()

MONGO_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.elevate_ai_db
history_collection = db.history

class HistoryItem(BaseModel):
    user_id: Optional[str] = "guest" # <--- Changed to Optional
    type: str
    name: str
    details: str
    date: str = datetime.now().strftime("%Y-%m-%d")

@router.post("/add")
async def add_history(item: HistoryItem):
    # Safety Check: If frontend sent null, force "guest"
    if item.user_id is None:
        item.user_id = "guest"
        
    await history_collection.insert_one(item.dict())
    return {"status": "success"}

@router.get("/get")
async def get_history(user_id: Optional[str] = "guest"):
    if user_id is None: user_id = "guest"
    
    cursor = history_collection.find({"user_id": user_id}).sort("_id", -1).limit(10)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results