#!/usr/bin/env python3
"""
BUG-C10: Python seed script for backend-python local development.

Creates sample data directly in MongoDB so developers can test without
running the full Python API first.

Usage:
    python scripts/seed.py

Requires MONGO_URI (or MONGODB_URI) in the backend-python/.env file,
or set as an environment variable. Refuses to run against 'prod' URIs.
"""

import os
import sys
from pathlib import Path

# Load .env from backend-python/
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_env_path, override=False)

MONGO_URI = os.environ.get("MONGO_URI") or os.environ.get("MONGODB_URI")

if not MONGO_URI:
    sys.exit("Error: MONGO_URI (or MONGODB_URI) environment variable is not set.")

if "prod" in MONGO_URI.lower():
    sys.exit("❌ Refusing to seed: MONGO_URI appears to point at a production database.")

try:
    from pymongo import MongoClient
except ImportError:
    sys.exit("Error: pymongo is not installed. Run: pip install pymongo")

from datetime import datetime, timezone

NOW = datetime.now(timezone.utc)

# ---------------------------------------------------------------------------
# Connect
# ---------------------------------------------------------------------------
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10_000)
db = client.get_default_database()
print(f"Connected to database: {db.name}")

# ---------------------------------------------------------------------------
# Clean previous seed data
# ---------------------------------------------------------------------------
for col_name in ("nutrition_plans", "workout_plans", "meal_progress"):
    result = db[col_name].delete_many({"__seed": True})
    print(f"Cleaned up {result.deleted_count} seed docs from '{col_name}'.")

# ---------------------------------------------------------------------------
# Sample nutrition plans
# ---------------------------------------------------------------------------
sample_nutrition = [
    {
        "__seed": True,
        "user_id": "seed_user_a",
        "email": "user_a@seed.local",
        "goal": "weight_loss",
        "calories_target": 1_600,
        "meals": {
            "breakfast": {
                "name": "Oats with Berries",
                "calories": 350,
                "items": [
                    {"name": "Rolled Oats", "quantity": "80g", "ticked": False, "tick_time": None},
                    {"name": "Blueberries", "quantity": "50g", "ticked": False, "tick_time": None},
                    {"name": "Almond Milk", "quantity": "200ml", "ticked": False, "tick_time": None},
                ]
            },
            "lunch": {
                "name": "Lentil Soup",
                "calories": 450,
                "items": [
                    {"name": "Red Lentils", "quantity": "100g", "ticked": False, "tick_time": None},
                    {"name": "Whole Grain Bread", "quantity": "2 slices", "ticked": False, "tick_time": None},
                ]
            },
            "dinner": {
                "name": "Grilled Tofu & Vegetables",
                "calories": 500,
                "items": [
                    {"name": "Firm Tofu", "quantity": "150g", "ticked": False, "tick_time": None},
                    {"name": "Mixed Stir-Fry Vegetables", "quantity": "200g", "ticked": False, "tick_time": None},
                    {"name": "Brown Rice", "quantity": "80g", "ticked": False, "tick_time": None},
                ]
            },
        },
        "created_at": NOW.isoformat(),
    }
]

# ---------------------------------------------------------------------------
# Sample workout plans
# ---------------------------------------------------------------------------
sample_workouts = [
    {
        "__seed": True,
        "user_id": "seed_user_b",
        "email": "user_b@seed.local",
        "goal": "strength",
        "experience": "advanced",
        "week": [
            {
                "day": "Monday",
                "focus": "Chest & Triceps",
                "exercises": [
                    {"name": "Barbell Bench Press", "sets": 4, "reps": 5, "rest_seconds": 180},
                    {"name": "Incline Dumbbell Press", "sets": 3, "reps": 8, "rest_seconds": 120},
                    {"name": "Tricep Dips", "sets": 3, "reps": 12, "rest_seconds": 90},
                ]
            },
            {
                "day": "Wednesday",
                "focus": "Back & Biceps",
                "exercises": [
                    {"name": "Deadlift", "sets": 4, "reps": 5, "rest_seconds": 240},
                    {"name": "Barbell Row", "sets": 3, "reps": 8, "rest_seconds": 120},
                    {"name": "Barbell Curl", "sets": 3, "reps": 10, "rest_seconds": 90},
                ]
            },
            {
                "day": "Friday",
                "focus": "Legs & Shoulders",
                "exercises": [
                    {"name": "Barbell Back Squat", "sets": 4, "reps": 5, "rest_seconds": 240},
                    {"name": "Romanian Deadlift", "sets": 3, "reps": 8, "rest_seconds": 120},
                    {"name": "Overhead Press", "sets": 3, "reps": 8, "rest_seconds": 120},
                ]
            }
        ],
        "created_at": NOW.isoformat(),
    }
]

# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------
if sample_nutrition:
    r = db["nutrition_plans"].insert_many(sample_nutrition)
    print(f"✅ Inserted {len(r.inserted_ids)} seed nutrition plan(s).")

if sample_workouts:
    r = db["workout_plans"].insert_many(sample_workouts)
    print(f"✅ Inserted {len(r.inserted_ids)} seed workout plan(s).")

print("\n🌱 Python seed complete. All docs tagged with __seed:True for easy cleanup.")
client.close()
