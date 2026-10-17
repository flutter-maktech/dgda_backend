from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ContentDocumentBase(BaseModel):
    title: str
    card_title: Optional[str] = None
    hero_title: Optional[str] = None
    subtitle: Optional[str] = None
    content: str
    paragraphs: List[str] = []
    last_updated: Optional[str] = None
    is_published: bool = True


class ContentDocumentCreate(ContentDocumentBase):
    id: Optional[str] = None
    type: str


class ContentDocumentUpdate(BaseModel):
    title: Optional[str] = None
    card_title: Optional[str] = None
    hero_title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    paragraphs: Optional[List[str]] = None
    last_updated: Optional[str] = None
    is_published: Optional[bool] = None


class ContentDocumentResponse(BaseModel):
    id: str
    type: str
    title: str
    card_title: Optional[str] = None
    hero_title: Optional[str] = None
    subtitle: Optional[str] = None
    content: str
    paragraphs: List[str] = []
    last_updated: Optional[str] = None
    is_published: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Aliases for Admin Dashboard
    @property
    def cardTitle(self) -> Optional[str]:
        return self.card_title

    @property
    def heroTitle(self) -> Optional[str]:
        return self.hero_title

    @property
    def lastUpdated(self) -> Optional[str]:
        return self.last_updated

    model_config = ConfigDict(from_attributes=True)


class ContentDocumentWrappedResponse(BaseModel):
    statusCode: int = 200
    success: bool = True
    message: str = "Document retrieved successfully"
    data: Optional[ContentDocumentResponse] = None
