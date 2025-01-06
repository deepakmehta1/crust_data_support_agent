from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import Conversation, Message
from app.config.db import conversations_collection
from pydantic import ValidationError


class ConversationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initializes the ConversationService with a MongoDB database connection.

        Args:
            db (AsyncIOMotorDatabase): The MongoDB database connection.
        """
        self.db = db
        self.conversations_collection = conversations_collection

    async def start_conversation(self, user_id: str) -> dict:
        """
        Starts a new conversation for a user and generates a conversation ID.

        Args:
            user_id (str): The ID of the user to start the conversation for.

        Returns:
            dict: A dictionary containing the message, conversation ID, and status.
        """
        conversation = Conversation(user_id=user_id, status="started", messages=[])
        result = await self.conversations_collection.insert_one(conversation.dict())
        conversation_id = str(result.inserted_id)
        return {
            "message": f"Conversation started for user {user_id}",
            "conversation_id": conversation_id,
            "status": "started",
        }

    async def store_message(
        self, conversation: Conversation, message_obj: Message, name: str = None
    ) -> bool:
        """
        Stores a message in an ongoing conversation.

        Args:
            conversation (Conversation): The conversation object containing the conversation details.
            message_obj (Message): The message object containing the message details.

        Returns:
            bool: True if the message was successfully stored, False otherwise.
        """
        try:
            conversation_update = {"$push": {"messages": message_obj.dict()}}
            await self.conversations_collection.update_one(
                {"_id": ObjectId(conversation.id)}, conversation_update
            )
            return True
        except Exception:
            return False

    async def get_conversation(self, conversation_id: str) -> dict:
        """
        Retrieves a conversation by its ID.

        Args:
            conversation_id (str): The ID of the conversation to retrieve.

        Returns:
            dict: A dictionary containing the conversation's details or an error message.
        """
        conversation = await self.conversations_collection.find_one(
            {"_id": ObjectId(conversation_id)}
        )

        if conversation:
            try:
                conversation_obj = Conversation(
                    user_id=conversation["user_id"],
                    status=conversation["status"],
                    messages=[
                        Message(**msg) for msg in conversation.get("messages", [])
                    ],
                )
                return conversation_obj.model_dump()
            except ValidationError as e:
                return {"error": f"Invalid data format: {e}"}
        else:
            return {"error": "Conversation not found"}
