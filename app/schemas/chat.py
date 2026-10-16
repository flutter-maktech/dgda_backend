from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=3000, description="The user's query or message")


class ChatMessageResponse(BaseModel):
    id: int
    role: str  # "user" or "assistant"
    content: str
    legal_reference: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
