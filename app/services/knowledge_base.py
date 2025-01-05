import motor.motor_asyncio
from typing import List, Dict
from bson import ObjectId
from app.models.knowledge_base import ApiDoc
from pymongo.errors import PyMongoError
from openai import OpenAI  # For generating vector embeddings
import numpy as np  # For calculating cosine similarity
from app.config.db import collection  # Import collection from mongo_config
import os

print("api_key:", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def insert_api_doc(api_doc: ApiDoc):
    try:
        # Generate the vector for the description using OpenAI's embeddings
        response = client.embeddings.create(
            input=api_doc.description, model="text-embedding-3-small"
        )
        description_vector = response.data[0].embedding

        # Insert the document along with the vector into MongoDB
        document = api_doc.model_dump(exclude_unset=True)
        document["vector"] = description_vector  # Add vector to document

        result = await collection.insert_one(document)
        return {"id": str(result.inserted_id), "message": "successfully inserted"}
    except PyMongoError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to generate vector: {str(e)}"}


async def search_api_doc(description_query: str) -> List[Dict]:
    try:
        # Generate the vector for the search query description using OpenAI's embeddings
        response = client.embeddings.create(
            input=description_query, model="text-embedding-ada-002"
        )
        query_vector = response.data[0].embedding  # Extract the embedding vector

        # Find similar documents based on vector search (we'll compute cosine similarity)
        cursor = collection.aggregate(
            [
                {
                    "$project": {
                        "name": 1,
                        "description": 1,
                        "data": 1,
                        "response": 1,
                        "vector": 1,  # Store the vector in your MongoDB documents
                    }
                },
                {
                    "$match": {
                        # Matching condition based on vector similarity (cosine similarity)
                        "$expr": {
                            "$gte": [
                                {
                                    "$function": {
                                        "body": """
                                    function(v1, v2) {
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
                                0.8,  # Set a threshold for similarity (0.8 means the descriptions are 80% similar)
                            ]
                        }
                    }
                },
            ]
        )
        return await cursor.to_list(length=10)  # Return top 10 matches

    except PyMongoError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to perform search: {str(e)}"}
