from pydantic import BaseModel


class StartConversationRequest(BaseModel):
    user_id: str


class SendMessageRequest(BaseModel):
    conversation_id: str
    user_id: str
    message: str
