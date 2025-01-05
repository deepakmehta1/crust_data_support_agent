import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Specify the path to your .env file
env_file_path = "app/.env"

# Load environment variables from .env file
load_dotenv(dotenv_path=env_file_path)


# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

if not MONGO_URI or not MONGO_DB or not MONGO_COLLECTION:
    print("Error: One or more MongoDB environment variables are missing!")
else:
    print("MongoDB configuration loaded successfully.")

# MongoDB client initialization
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]
