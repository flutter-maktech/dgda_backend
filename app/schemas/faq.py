from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FAQBase(BaseModel):
    no: Optional[int] = 1
    question: str
    answer: str
    status: str = "ACTIVE"  # ACTIVE, INACTIVE
    category: str = "General"


class FAQCreate(FAQBase):
    id: Optional[str] = None


class FAQUpdate(BaseModel):
    no: Optional[int] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None


class FAQResponse(FAQBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
