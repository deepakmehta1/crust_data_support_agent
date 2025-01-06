from app.services.conversation import ConversationService
from fastapi import Depends
from app.services.knowledge_base import insert_api_doc, search_api_doc
from app.config.db import db
from app.agent.agent import Agent
from app.agent.config import generate_system_prompt
from app.models import SendMessageRequest


# Dependency provider for ConversationService
def get_conversation_service():
    return ConversationService(db)


# Dependency provider for the Knowledge Base service functions
def get_insert_api_doc():
    return insert_api_doc


def get_search_api_doc():
    return search_api_doc


# Dependency provider for the Agent
async def get_agent(
    request: SendMessageRequest,  # Use the request object to get message and conversation_id
    conversation_service: ConversationService = Depends(get_conversation_service),
    search_api_doc: callable = Depends(
        get_search_api_doc
    ),  # Dependency for searching knowledge base
):
    # Use the user message to search the knowledge base for relevant context
    knowledge_base_results = await search_api_doc(
        request.message
    )  # This will return relevant API information

    # Generate the system prompt dynamically using the knowledge base
    system_prompt = generate_system_prompt(knowledge_base_results[0])

    # Create the agent instance using the generated system prompt and conversation data
    return Agent(
        system_prompt=system_prompt,
        conversation_id=request.conversation_id,
        conversation_service=conversation_service,
    )
