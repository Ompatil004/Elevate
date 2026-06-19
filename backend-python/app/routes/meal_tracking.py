from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List
from app.db import get_database

router = APIRouter(prefix="/api/meals", tags=["meal-tracking"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _meal_progress_col():
    return get_database()["meal_progress"]


def _meal_history_col():
    return get_database()["meal_history"]


class InitDayRequest(BaseModel):
    user_id: str
    date: str
    meal_plan: dict


class TickItemRequest(BaseModel):
    user_id: str
    date: str
    meal_type: str
    item_index: int
    ticked: bool


@router.post("/init-day")
async def init_day_meals(req: InitDayRequest):
    """Initialize a day's meal plan with tickable items"""
    meal_progress_col = _meal_progress_col()
    existing = await meal_progress_col.find_one({"user_id": req.user_id, "date": req.date})
    if existing:
        existing.pop("_id", None)
        return {"status": "ok", "data": existing.get("meals", {})}

    meals_data = {}
    for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
        if meal_type in req.meal_plan:
            items = req.meal_plan[meal_type].get("items", [])
            meals_data[meal_type] = {
                "name": req.meal_plan[meal_type].get("name", ""),
                "calories": req.meal_plan[meal_type].get("calories", 0),
                "items": [
                    {"name": item.get("name", ""), "quantity": item.get("quantity", ""), "ticked": False, "tick_time": None}
                    for item in items
                ],
                "locked": False,
                "completed_at": None,
            }

    await meal_progress_col.insert_one({"user_id": req.user_id, "date": req.date, "meals": meals_data})
    return {"status": "ok", "data": meals_data}


@router.post("/tick-item")
async def tick_item(req: TickItemRequest):
    """Tick/untick a meal item. Cannot modify if meal is locked."""
    # Bug #14 fixed: use atomic $set directly on the specific array element
    # to avoid the read-modify-write race condition.  We first validate the
    # document exists and that the item index is in range, then apply an
    # atomic update using dot-notation for the nested array position.
    meal_progress_col = _meal_progress_col()

    # Lightweight validation read (only fetches the fields we need)
    doc = await meal_progress_col.find_one(
        {"user_id": req.user_id, "date": req.date},
        {"meals": 1},
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Day not initialized")

    meals = doc.get("meals", {})
    if req.meal_type not in meals:
        raise HTTPException(status_code=404, detail=f"Meal type '{req.meal_type}' not found")

    meal = meals[req.meal_type]
    if meal.get("locked"):
        raise HTTPException(status_code=400, detail="Meal is locked. All items were completed.")

    items = meal.get("items", [])
    if req.item_index < 0 or req.item_index >= len(items):
        raise HTTPException(status_code=400, detail="Invalid item index")

    # Bug #31 fixed: use timezone-aware UTC timestamps for consistency
    tick_time = _utcnow().strftime("%I:%M %p UTC") if req.ticked else None

    # Atomic update of just the specific item fields
    item_base = f"meals.{req.meal_type}.items.{req.item_index}"
    update_fields = {
        f"{item_base}.ticked": req.ticked,
        f"{item_base}.tick_time": tick_time,
    }

    # Optimistically set updated fields
    items[req.item_index]["ticked"] = req.ticked
    items[req.item_index]["tick_time"] = tick_time

    all_ticked = all(item["ticked"] for item in items) and len(items) > 0
    if all_ticked:
        completed_at = _utcnow().isoformat()
        update_fields[f"meals.{req.meal_type}.locked"] = True
        update_fields[f"meals.{req.meal_type}.completed_at"] = completed_at
        meal["locked"] = True
        meal["completed_at"] = completed_at

    await meal_progress_col.update_one(
        {"user_id": req.user_id, "date": req.date},
        {"$set": update_fields},
    )

    if all_ticked:
        await _save_to_history(req.user_id, req.date, req.meal_type, meal)

    return {"status": "ok", "meal": meal, "all_ticked": all_ticked, "locked": meal.get("locked", False)}


@router.get("/day-progress")
async def get_day_progress(user_id: str, date: str):
    meal_progress_col = _meal_progress_col()
    doc = await meal_progress_col.find_one({"user_id": user_id, "date": date})
    if doc:
        doc.pop("_id", None)
    return {"status": "ok", "data": doc.get("meals", {}) if doc else {}}


@router.get("/history")
async def get_meal_history(user_id: str):
    meal_history_col = _meal_history_col()
    entries = await meal_history_col.find({"user_id": user_id}).sort("date", -1).to_list(length=365)
    for e in entries:
        e.pop("_id", None)
    return {"status": "ok", "data": entries}


@router.get("/history/{date}")
async def get_meal_history_by_date(user_id: str, date: str):
    meal_history_col = _meal_history_col()
    entry = await meal_history_col.find_one({"user_id": user_id, "date": date})
    if not entry:
        raise HTTPException(status_code=404, detail="No history for this date")
    entry.pop("_id", None)
    return {"status": "ok", "data": entry}


async def _save_to_history(user_id: str, date: str, meal_type: str, meal: dict):
    """Atomically upsert a completed meal into the history collection.
    
    Bug #14 fixed: replaced the find-then-insert+update pattern with a single
    atomic upsert to avoid races between the existence check and the insert.
    The $inc on total_calories also avoids the stale-read problem.
    """
    meal_history_col = _meal_history_col()
    meal_calories = meal.get("calories", 0)

    # Upsert the document and set the completed meal atomically
    await meal_history_col.update_one(
        {"user_id": user_id, "date": date},
        {
            "$set": {
                f"meals.{meal_type}": {
                    "name": meal.get("name", ""),
                    "calories": meal_calories,
                    "items": meal.get("items", []),
                    "completed_at": meal.get("completed_at"),
                }
            },
            "$inc": {"total_calories": meal_calories},
            "$setOnInsert": {
                "created_at": _utcnow().isoformat(),
            },
        },
        upsert=True,
    )
