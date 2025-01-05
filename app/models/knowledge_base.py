from pydantic import BaseModel
from typing import Optional, Dict


class ApiDoc(BaseModel):
    name: str
    description: str
    data: Optional[Dict[str, str]] = None  # Optional key-value pairs


class ApiDocInResponse(BaseModel):
    name: str
    description: str
    data: Optional[Dict[str, str]]
