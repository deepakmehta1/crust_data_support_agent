import motor.motor_asyncio
from typing import List, Dict
from bson import ObjectId
from app.models.knowledge_base import ApiDoc
from pymongo.errors import PyMongoError
from openai import OpenAI
import numpy as np
from app.config.db import collection
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def cosine_similarity(v1, v2):
    """
    Computes the cosine similarity between two vectors.

    Args:
        v1 (numpy.ndarray): The first vector.
        v2 (numpy.ndarray): The second vector.

    Returns:
        float: The cosine similarity score.
    """
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)


async def insert_api_doc(api_doc: ApiDoc):
    """
    Inserts a new API document into MongoDB along with its vector embedding.

    Args:
        api_doc (ApiDoc): The API document to insert.

    Returns:
        dict: A dictionary with the result of the insertion or an error message.
    """
    try:
        response = client.embeddings.create(
            input=api_doc.description, model="text-embedding-3-small"
        )
        description_vector = response.data[0].embedding

        document = api_doc.model_dump(exclude_unset=True)
        document["vector"] = description_vector

        result = await collection.insert_one(document)
        return {"id": str(result.inserted_id), "message": "successfully inserted"}
    except PyMongoError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to generate vector: {str(e)}"}


async def search_api_doc(description_query: str, top_n: int = 10) -> List[Dict]:
    """
    Searches for similar API documents based on a query description using vector similarity.

    Args:
        description_query (str): The query description to search for.
        top_n (int, optional): The number of top similar documents to return. Defaults to 10.

    Returns:
        List[Dict]: A list of the top similar documents with their similarity scores.
    """
    try:
        response = client.embeddings.create(
            input=description_query, model="text-embedding-ada-002"
        )
        query_vector = response.data[0].embedding

        cursor = collection.find(
            {}, {"name": 1, "description": 1, "data": 1, "response": 1, "vector": 1}
        )

        results_with_scores = []

        async for document in cursor:
            doc_vector = document.get("vector")
            if doc_vector:
                score = cosine_similarity(np.array(query_vector), np.array(doc_vector))
                results_with_scores.append((document, score))

        results_with_scores.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, score in results_with_scores[:top_n]]

    except PyMongoError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to perform search: {str(e)}"}
