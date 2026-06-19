#!/usr/bin/env python3
"""
Create MongoDB indexes for optimal query performance

Run with: python scripts/create_indexes.py
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

MONGODB_URL = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/elevate_fitness")

async def create_indexes():
    """Create all necessary MongoDB indexes"""
    print("=" * 60)
    print("MongoDB Index Creation Script")
    print("=" * 60)
    print(f"\nConnecting to: {MONGODB_URL}\n")
    
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection established\n")
        
        db = client.get_database()
        
        # Users collection
        print("Creating indexes for 'users' collection...")
        await db.users.create_index("email", unique=True)
        await db.users.create_index("googleId", unique=True, sparse=True)
        await db.users.create_index("lastLoginAt", -1)
        await db.users.create_index("createdAt", -1)
        print("  ✅ email (unique)")
        print("  ✅ googleId (unique, sparse)")
        print("  ✅ lastLoginAt (descending)")
        print("  ✅ createdAt (descending)")
        print()

        # Weekly workout metadata / swap tracking
        print("Creating indexes for workout swap metadata...")
        await db.users.create_index("workoutWeekMetadata.week_start_date")
        await db.users.create_index("workoutWeekMetadata.updated_at")
        print("  ✅ users.workoutWeekMetadata.week_start_date")
        print("  ✅ users.workoutWeekMetadata.updated_at")
        print()
        
        # User daily logs
        print("Creating indexes for 'user_daily_logs' collection...")
        await db.user_daily_logs.create_index([("user_id", 1), ("date", -1)])
        await db.user_daily_logs.create_index("date", -1)
        print("  ✅ user_id + date (compound)")
        print("  ✅ date (descending)")
        print()
        
        # Weight logs
        print("Creating indexes for 'user_weight_logs' collection...")
        await db.user_weight_logs.create_index([("user_id", 1), ("recorded_at", -1)])
        print("  ✅ user_id + recorded_at (compound)")
        print()
        
        # Plan regenerations
        print("Creating indexes for 'user_plan_regenerations' collection...")
        await db.user_plan_regenerations.create_index([("user_id", 1), ("createdAt", -1)])
        await db.user_plan_regenerations.create_index("trigger_type")
        print("  ✅ user_id + createdAt (compound)")
        print("  ✅ trigger_type")
        print()
        
        # Workout history
        print("Creating indexes for 'user_workout_history' collection...")
        await db.user_workout_history.create_index([("user_id", 1), ("completed_at", -1)])
        print("  ✅ user_id + completed_at (compound)")
        print()
        
        # Meal history
        print("Creating indexes for 'user_meal_history' collection...")
        await db.user_meal_history.create_index([("user_id", 1), ("consumed_at", -1)])
        print("  ✅ user_id + consumed_at (compound)")
        print()
        
        # Activity logs
        print("Creating indexes for 'user_activity' collection...")
        await db.user_activity.create_index([("user_id", 1), ("timestamp", -1)])
        await db.user_activity.create_index([("activity_type", 1), ("timestamp", -1)])
        print("  ✅ user_id + timestamp (compound)")
        print("  ✅ activity_type + timestamp (compound)")
        print()

        # Swap audit logs
        print("Creating indexes for 'swap_history' collection...")
        await db.swap_history.create_index([("user_id", 1), ("week_start_date", 1), ("performed_at", -1)])
        await db.swap_history.create_index([("swap_type", 1), ("performed_at", -1)])
        print("  ✅ user_id + week_start_date + performed_at (compound)")
        print("  ✅ swap_type + performed_at (compound)")
        print()
        
        print("=" * 60)
        print("✅ All indexes created successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error creating indexes: {e}")
        print("\nMake sure MongoDB is running and accessible.")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_indexes())
