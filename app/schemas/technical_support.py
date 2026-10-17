from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TechnicalSupportInfoBase(BaseModel):
    title: str = "Assistance DGDA 24h/24 et 7j/7"
    description: str
    phone_numbers: str = "+243 81 700 0001 / +243 99 800 0002"
    phone_list: List[str] = ["+243817000001", "+243998000002"]
    email: str = "support.sydonia@dgda.gouv.cd"
    whatsapp: Optional[str] = "+243821920215"
    portal_url: Optional[str] = "https://douane.gouv.cd/assistance"
    operating_hours: str = "24/7 - Service Continu"
    is_active: bool = True


class TechnicalSupportInfoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    phone_numbers: Optional[str] = None
    phone_list: Optional[List[str]] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    portal_url: Optional[str] = None
    operating_hours: Optional[str] = None
    is_active: Optional[bool] = None


class TechnicalSupportInfoResponse(TechnicalSupportInfoBase):
    id: str = "dgda-helpdesk"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SupportTicketCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    subject: str
    category: str = "SydoniaWorld"
    message: str


class SupportTicketUpdate(BaseModel):
    status: Optional[str] = None  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority: Optional[str] = None  # NORMAL, HIGH, URGENT
    admin_notes: Optional[str] = None


class SupportTicketResponse(BaseModel):
    id: str
    ticket_number: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    subject: str
    category: str
    message: str
    status: str
    priority: str
    admin_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
