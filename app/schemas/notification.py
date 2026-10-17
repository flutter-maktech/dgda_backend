from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    body: str
    target_audience: Optional[str] = "All Users"
    category: Optional[str] = "Operational Alert"
    priority: Optional[str] = "Normal Priority"
    sent_at: Optional[str] = None
    audience_reach: Optional[str] = "Tous les usagers"
    open_rate: Optional[str] = "0%"
    status: Optional[str] = "delivered"


class NotificationCreate(NotificationBase):
    id: Optional[str] = None


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None
    target_audience: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    sent_at: Optional[str] = None
    audience_reach: Optional[str] = None
    open_rate: Optional[str] = None
    status: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    body: str
    target_audience: str
    category: str
    priority: str
    sent_at: Optional[str] = None
    audience_reach: str
    open_rate: str
    status: str
    is_read: bool = False
    is_unread: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Aliases for Flutter mobile app & Admin Dashboard
    @property
    def message(self) -> str:
        return self.body

    @property
    def targetAudience(self) -> str:
        return self.target_audience

    @property
    def sentAt(self) -> Optional[str]:
        return self.sent_at

    @property
    def audienceReach(self) -> str:
        return self.audience_reach

    @property
    def openRate(self) -> str:
        return self.open_rate

    model_config = ConfigDict(from_attributes=True)
