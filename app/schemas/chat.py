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


class KnowledgeEntryBase(BaseModel):
    question: str
    category: str
    legal_reference: str
    official_answer: str
    keywords: Optional[List[str]] = None
    confidence: Optional[int] = 95
    status: Optional[str] = "active"


class KnowledgeEntryCreate(KnowledgeEntryBase):
    pass


class KnowledgeEntryUpdate(BaseModel):
    question: Optional[str] = None
    category: Optional[str] = None
    legal_reference: Optional[str] = None
    official_answer: Optional[str] = None
    keywords: Optional[List[str]] = None
    confidence: Optional[int] = None
    status: Optional[str] = None


class KnowledgeEntryResponse(BaseModel):
    id: str
    question: str
    category: str
    legal_reference: str
    legalReference: Optional[str] = None
    official_answer: str
    officialAnswer: Optional[str] = None
    keywords: List[str] = []
    confidence: int = 95
    status: str = "active"
    updated_at: str
    updatedAt: Optional[str] = None


class TestAgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)


class TestAgentQueryResponse(BaseModel):
    query: str
    reply: str
    category: str
    legal_reference: Optional[str] = None
    legalReference: Optional[str] = None
    officialAnswer: Optional[str] = None
    confidence: int
    matched_id: Optional[str] = None
