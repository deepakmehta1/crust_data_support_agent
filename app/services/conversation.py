class MockConversationService:
    def start_conversation(self, user_id: str) -> dict:
        return {"message": f"Conversation started for user {user_id}", "status": "started"}

    def send_message(self, user_id: str, message: str) -> dict:
        return {"user_id": user_id, "message": message, "response": f"Echo: {message}", "status": "message_sent"}

# Initialize the service
conversation_service = MockConversationService()