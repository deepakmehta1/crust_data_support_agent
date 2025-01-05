from pydantic import BaseModel

class StartConversationRequest(BaseModel):
    user_id: str

class SendMessageRequest(BaseModel):
    user_id: str
    message: str

class SendMessageResponse(BaseModel):
    user_id: str
    message: str
    response: str
    status: str