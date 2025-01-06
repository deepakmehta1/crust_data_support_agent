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
    request: SendMessageRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    return await Agent.create(
        generate_system_prompt(), request.conversation_id, conversation_service
    )
