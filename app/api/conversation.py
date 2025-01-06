from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_conversation_service, get_agent
from app.agent.agent import Agent
from app.services.conversation import ConversationService
from app.models import (
    StartConversationRequest,
    SendMessageRequest,
    SendMessageResponse,
)

router = APIRouter()


# Start conversation endpoint using dependency injection
@router.post("/start", response_model=dict)
async def start_conversation(
    request: StartConversationRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """
    Starts a new conversation for the user and returns the conversation ID.
    """
    try:
        result = await conversation_service.start_conversation(request.user_id)
        return {
            "message": result["message"],
            "conversation_id": result["conversation_id"],
            "status": result["status"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting conversation: {str(e)}"
        )


@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    agent: Agent = Depends(get_agent),
):
    """
    Sends a message in an ongoing conversation identified by conversation_id.
    """
    try:
        # Using agent to interact with the user
        agent_response = await agent.interact(request.message)
        return SendMessageResponse(agent=agent_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")
