from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone


class Message(BaseModel):
    user_id: str
    message: str
    response: str
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conversation(BaseModel):
    user_id: str
    status: str
    messages: List[Message] = []
