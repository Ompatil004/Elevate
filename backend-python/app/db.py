import os
from motor.motor_asyncio import AsyncIOMotorClient


# MongoDB connection settings
MONGODB_URL = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/elevate_fitness")

# Global client variable
client: AsyncIOMotorClient = None


def _is_local_mongo_uri(uri: str) -> bool:
    normalized = str(uri or '').lower()
    return 'localhost' in normalized or '127.0.0.1' in normalized or '::1' in normalized


def _validate_mongo_security(uri: str) -> None:
    env = os.getenv('NODE_ENV', os.getenv('PYTHON_ENV', '')).lower()
    if env != 'production':
        return

    insecure = str(uri or '').startswith('mongodb://') and not _is_local_mongo_uri(uri)
    allow_insecure = os.getenv('ALLOW_INSECURE_MONGO', '0').strip() == '1'

    if insecure and not allow_insecure:
        raise RuntimeError(
            'Insecure Mongo URI detected for production. Use mongodb+srv:// (TLS) '
            'or set ALLOW_INSECURE_MONGO=1 only for controlled private networks.'
        )

    if insecure and allow_insecure:
        print('WARNING: ALLOW_INSECURE_MONGO=1 enabled in production; ensure private network controls are in place.')

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client
    try:
        _validate_mongo_security(MONGODB_URL)
        client = AsyncIOMotorClient(MONGODB_URL)
        # Test the connection
        await client.admin.command('ping')
        print("MongoDB connection established")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print(" MongoDB connection closed")

def get_database():
    """Get the database instance"""
    if client is None:
        raise RuntimeError("MongoDB client not initialized. Call connect_to_mongo first.")

    # Extract database name from the connection string
    # Handle different MongoDB URI formats
    if MONGODB_URL.startswith("mongodb://"):
        # Format: mongodb://host:port/database_name
        # or mongodb://username:password@host:port/database_name
        path_parts = MONGODB_URL.split('/')
        if len(path_parts) >= 4:
            db_name = path_parts[3]
            # Remove query parameters if present
            if '?' in db_name:
                db_name = db_name.split('?')[0]
        else:
            db_name = "elevate_fitness"  # default
    elif MONGODB_URL.startswith("mongodb+srv://"):
        # Format: mongodb+srv://host/database_name
        path_parts = MONGODB_URL.split('/')
        if len(path_parts) >= 4:
            db_name = path_parts[3]
            # Remove query parameters if present
            if '?' in db_name:
                db_name = db_name.split('?')[0]
        else:
            db_name = "elevate_fitness"  # default
    else:
        # Fallback: extract from custom format
        import re
        match = re.search(r'/([^/\?]+)', MONGODB_URL)
        if match:
            db_name = match.group(1)
            # Remove query parameters if present
            if '?' in db_name:
                db_name = db_name.split('?')[0]
        else:
            db_name = "elevate_fitness"  # default

    # Ensure the database name is valid (doesn't contain dots)
    if '.' in db_name:
        # If database name contains dots, use the default
        db_name = "elevate_fitness"

    return client[db_name]

def get_user_collection():
    """Get the user collection instance"""
    db = get_database()
    return db.users

def get_workout_history_collection():
    """Get the workout history collection instance"""
    db = get_database()
    return db.workout_history

def get_meal_history_collection():
    """Get the meal history collection instance"""
    db = get_database()
    return db.meal_history

def get_workout_completion_collection():
    """Get the workout completion collection instance"""
    db = get_database()
    return db.workout_completions

def get_meal_completion_collection():
    """Get the meal completion collection instance"""
    db = get_database()
    return db.meal_completions

def get_weekly_meal_plans_collection():
    """Get the weekly meal plans collection instance"""
    db = get_database()
    return db.weekly_meal_plans