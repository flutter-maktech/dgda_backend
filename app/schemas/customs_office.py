from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CustomsOfficeBase(BaseModel):
    code: str = "[CDMAT]"
    name: str
    subtitle: str = "Primary Maritime Port"
    office_location: str
    working_hours: str = "24/7 Commercial Corridors"
    station_code: str = "CD-STN-421"
    region: str = "Kongo Central"
    authority: str = "Inspecteur Principal"
    juxtaposed_post: Optional[str] = None
    tags: str = "Import,Export,Transit,Maritime Port"
    phone: str = "+243 81 234 5678"
    is_open: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CustomsOfficeCreate(CustomsOfficeBase):
    pass


class CustomsOfficeUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    subtitle: Optional[str] = None
    office_location: Optional[str] = None
    working_hours: Optional[str] = None
    station_code: Optional[str] = None
    region: Optional[str] = None
    authority: Optional[str] = None
    juxtaposed_post: Optional[str] = None
    tags: Optional[str] = None
    phone: Optional[str] = None
    is_open: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CustomsOfficeResponse(CustomsOfficeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
