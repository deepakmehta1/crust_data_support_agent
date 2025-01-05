from pydantic import BaseModel
from typing import Optional, Dict, Any


class ApiDoc(BaseModel):
    name: str
    description: str
    data: Any = None  # Optional key-value pairs
    response: Any  # Required key-value pairs


class ApiDocInResponse(BaseModel):
    name: str
    description: str
    data: Any
    response: Any


class SuccessResponse(BaseModel):
    message: str
    status: bool
