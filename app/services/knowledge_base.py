import motor.motor_asyncio
from typing import List, Dict
from bson import ObjectId
from app.models.knowledge_base import ApiDoc
from pymongo.errors import PyMongoError
import openai  # If you're using OpenAI's embeddings API for vector search

# MongoDB client initialization
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client["knowledge_base_db"]  # Use the desired database
collection = db["api_doc"]  # Collection to store API docs

# Vector Search Setup (Assume you're using OpenAI's Embeddings API for vector search)
openai.api_key = "your-openai-api-key"  # Set your OpenAI API key here


async def insert_api_doc(api_doc: ApiDoc):
    try:
        # Insert the document into MongoDB
        document = api_doc.dict(exclude_unset=True)
        result = await collection.insert_one(document)
        return {"id": str(result.inserted_id), "message": "Document inserted"}
    except PyMongoError as e:
        return {"error": str(e)}


async def search_api_doc(description_query: str) -> List[Dict]:
    try:
        # Generate the vector for the description using OpenAI's embeddings
        response = openai.Embedding.create(
            input=description_query, model="text-embedding-ada-002"
        )
        query_vector = response["data"][0]["embedding"]

        # Find similar documents based on vector search (assumes stored vectors)
        cursor = collection.aggregate(
            [
                {
                    "$project": {
                        "name": 1,
                        "description": 1,
                        "data": 1,
                        "vector": 1,  # Store the vector in your MongoDB documents
                    }
                },
                {
                    "$match": {
                        # Matching condition based on vector similarity
                        "$expr": {
                            "$gte": [
                                {
                                    "$function": {
                                        "body": """
                                    function(v1, v2) {
                                        // Compute cosine similarity or distance
                                        const dot_product = v1.reduce((sum, val, idx) => sum + val * v2[idx], 0);
                                        const magnitude_v1 = Math.sqrt(v1.reduce((sum, val) => sum + val * val, 0));
                                        const magnitude_v2 = Math.sqrt(v2.reduce((sum, val) => sum + val * val, 0));
                                        return dot_product / (magnitude_v1 * magnitude_v2); 
                                    }
                                """,
                                        "args": ["$vector", query_vector],
                                        "lang": "js",
                                    }
                                },
                                0.8,  # Set a threshold for similarity
                            ]
                        }
                    }
                },
            ]
        )
        return await cursor.to_list(length=10)  # Return top 10 matches

    except PyMongoError as e:
        return {"error": str(e)}
