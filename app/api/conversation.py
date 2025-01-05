from fastapi import APIRouter, Depends, HTTPException
from ..models.conversation import (
    StartConversationRequest,
    SendMessageRequest,
    SendMessageResponse,
)
from ..dependencies import get_conversation_service
from ..services.conversation import ConversationService

router = APIRouter()


# Start conversation endpoint using dependency injection
@router.post("/start", response_model=dict)
async def start_conversation(
    request: StartConversationRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    try:
        result = conversation_service.start_conversation(request.user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting conversation: {str(e)}"
        )


# Send message endpoint using dependency injection
@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    try:
        result = conversation_service.send_message(request.user_id, request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")
