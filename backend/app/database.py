from pymongo import MongoClient

# 1. Connect to MongoDB (Default Localhost)
# If you use a Cloud URL, paste it inside the quotes below
MONGO_URI = "mongodb://localhost:27017/" 

client = MongoClient(MONGO_URI)

# 2. Create the Database
db = client["elevate_ai_db"]

# 3. Create Collections (Tables)
users_collection = db["users"]
history_collection = db["history"]

print("✔ Connected to MongoDB")