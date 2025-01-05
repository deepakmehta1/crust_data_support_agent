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
MONGO_API_DOC_COLLECTION = os.getenv("MONGO_API_DOC_COLLECTION")
MONGO_CONVERSATIONS_COLLECTION = os.getenv("MONGO_CONVERSATIONS_COLLECTION")

if (
    not MONGO_URI
    or not MONGO_DB
    or not MONGO_API_DOC_COLLECTION
    or not MONGO_CONVERSATIONS_COLLECTION
):
    print("Error: One or more MongoDB environment variables are missing!")
else:
    print("MongoDB configuration loaded successfully.")

# MongoDB client initialization
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
api_doc_collection = db[MONGO_API_DOC_COLLECTION]
conversations_collection = db[MONGO_CONVERSATIONS_COLLECTION]
