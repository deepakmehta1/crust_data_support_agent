from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from bson import ObjectId
from app.models import Conversation, Message
from app.config.db import conversations_collection


class ConversationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.conversations_collection = conversations_collection

    async def start_conversation(self, user_id: str) -> dict:
        """
        Starts a new conversation for a user and generates a conversation ID.
        """
        conversation = Conversation(user_id=user_id, status="started", messages=[])

        result = await self.conversations_collection.insert_one(conversation.dict())
        conversation_id = str(result.inserted_id)
        return {
            "message": f"Conversation started for user {user_id}",
            "conversation_id": conversation_id,
            "status": "started",
        }

    async def send_message(
        self, conversation_id: str, user_id: str, message: str
    ) -> dict:
        """
        Sends a message in an ongoing conversation.
        """
        agent_response = f"Echo: {message}"

        message_obj = Message(
            user_id=user_id,
            message=message,
            response=agent_response,
            status="message_sent",
            timestamp=datetime.now(timezone.utc),
        )

        conversation_update = {"$push": {"messages": message_obj.model_dump()}}

        await self.conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)}, conversation_update
        )

        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "message": message,
            "response": agent_response,
            "status": "message_sent",
            "timestamp": message_obj.timestamp.isoformat(),
        }

    async def get_conversation(self, conversation_id: str) -> dict:
        """
        Retrieves a conversation by its ID.
        """
        conversation = await self.conversations_collection.find_one(
            {"_id": ObjectId(conversation_id)}
        )
        if conversation:
            conversation_obj = Conversation(**conversation)
            return {
                "conversation_id": conversation_id,
                "messages": conversation_obj.messages,
                "status": conversation_obj.status,
            }
        else:
            return {"error": "Conversation not found"}
