from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.config.db import conversations_collection


class ConversationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.conversations_collection = conversations_collection

    async def start_conversation(self, user_id: str) -> dict:
        """
        Starts a new conversation for a user and generates a conversation ID.

        Args:
            user_id (str): The ID of the user starting the conversation.

        Returns:
            dict: The response with a message and the conversation ID.
        """
        conversation = {
            "user_id": user_id,
            "messages": [],
            "status": "started",
        }
        result = await self.conversations_collection.insert_one(conversation)
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

        Args:
            conversation_id (str): The ID of the ongoing conversation.
            user_id (str): The ID of the user sending the message.
            message (str): The message content from the user.

        Returns:
            dict: The response with the sent message and its echo response.
        """
        # Hardcoding the agent's response as same as the user message for now
        agent_response = f"Echo: {message}"

        # Append the message to the conversation's message list
        conversation_update = {
            "$push": {
                "messages": {
                    "user_id": user_id,
                    "message": message,
                    "response": agent_response,
                    "status": "message_sent",
                }
            }
        }
        await self.conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)}, conversation_update
        )

        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "message": message,
            "response": agent_response,
            "status": "message_sent",
        }

    async def get_conversation(self, conversation_id: str) -> dict:
        """
        Retrieves a conversation by its ID.

        Args:
            conversation_id (str): The ID of the conversation to retrieve.

        Returns:
            dict: The conversation details.
        """
        conversation = await self.conversations_collection.find_one(
            {"_id": ObjectId(conversation_id)}
        )
        if conversation:
            return {
                "conversation_id": conversation_id,
                "messages": conversation["messages"],
                "status": conversation["status"],
            }
        else:
            return {"error": "Conversation not found"}
