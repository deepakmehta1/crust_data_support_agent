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


# Function to compute cosine similarity between two vectors
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)


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


async def search_api_doc(description_query: str, top_n: int = 10) -> List[Dict]:
    try:
        # Generate the vector for the search query description using OpenAI's embeddings
        response = client.embeddings.create(
            input=description_query, model="text-embedding-ada-002"
        )
        query_vector = response.data[0].embedding  # Extract the embedding vector

        # Fetch documents from MongoDB
        cursor = collection.find(
            {}, {"name": 1, "description": 1, "data": 1, "response": 1, "vector": 1}
        )

        # List to hold documents with similarity scores
        results_with_scores = []

        async for document in cursor:
            # Calculate cosine similarity between query vector and document's vector
            doc_vector = document.get("vector")
            if doc_vector:
                score = cosine_similarity(np.array(query_vector), np.array(doc_vector))
                results_with_scores.append((document, score))

        # Sort results by cosine similarity score in descending order
        results_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top_n matches
        return [doc for doc, score in results_with_scores[:top_n]]

    except PyMongoError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to perform search: {str(e)}"}
