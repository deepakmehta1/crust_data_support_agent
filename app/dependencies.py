from app.services.conversation import ConversationService


# Dependency provider for ConversationService
def get_conversation_service():
    return ConversationService()
