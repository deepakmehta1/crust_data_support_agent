from app.services.conversation import ConversationService
from app.services.knowledge_base import insert_api_doc, search_api_doc
from app.config.db import db


# Dependency provider for ConversationService
def get_conversation_service():
    return ConversationService(db)


# Dependency provider for the Knowledge Base service functions
def get_insert_api_doc():
    return insert_api_doc


def get_search_api_doc():
    return search_api_doc
