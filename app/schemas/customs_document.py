from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CustomsDocumentBase(BaseModel):
    title: str
    category: str = "Procedures & Forms"
    format: str = "PDF"
    file_size: str = "2.4 MB"
    date: str = "Août 2024"
    download_url: str
    image_url: Optional[str] = None
    description: Optional[str] = None


class CustomsDocumentCreate(CustomsDocumentBase):
    pass


class CustomsDocumentUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    format: Optional[str] = None
    file_size: Optional[str] = None
    date: Optional[str] = None
    download_url: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


class CustomsDocumentResponse(CustomsDocumentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
