from fastapi import APIRouter, HTTPException
from ..services.conversation import conversation_service
from ..models.conversation import (
    StartConversationRequest,
    SendMessageRequest,
    SendMessageResponse,
)

router = APIRouter()


# Endpoint to start conversation
@router.post("/start", response_model=dict)
async def start_conversation(request: StartConversationRequest):
    try:
        result = conversation_service.start_conversation(request.user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting conversation: {str(e)}"
        )


# Endpoint to send message
@router.post("/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    try:
        result = conversation_service.send_message(request.user_id, request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")
