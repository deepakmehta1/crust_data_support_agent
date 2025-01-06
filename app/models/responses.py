from pydantic import BaseModel
from typing import Any


class ApiDocInResponse(BaseModel):
    name: str
    description: str
    data: Any
    response: Any


class SuccessResponse(BaseModel):
    message: str
    status: bool


class SendMessageResponse(BaseModel):
    conversation_id: str
    user_id: str
    message: str
    response: str
    status: str
    timestamp: str
