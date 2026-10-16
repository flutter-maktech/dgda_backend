from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CalendarEventBase(BaseModel):
    title: str = "Physical Inspection"
    category: str = "Forwarder Meeting"
    reference_code: Optional[str] = None
    referenceCode: Optional[str] = None
    location: str = "Matadi Port Customs Office"
    event_date: Optional[str] = None
    eventDate: Optional[str] = None
    date: Optional[str] = None
    time_slot: Optional[str] = None
    timeSlot: Optional[str] = None
    time: Optional[str] = None
    reminder_date: Optional[str] = None
    reminderDate: Optional[str] = None
    reminder_time: Optional[str] = None
    reminderTime: Optional[str] = None
    description: Optional[str] = None
    status: str = "scheduled"

    def get_event_date(self) -> str:
        return self.event_date or self.eventDate or self.date or datetime.now().strftime("%Y-%m-%d")

    def get_time_slot(self) -> str:
        return self.time_slot or self.timeSlot or self.time or "10:00 AM"

    def get_reference_code(self) -> str:
        return self.reference_code or self.referenceCode or ""

    def get_reminder_date(self) -> str:
        return self.reminder_date or self.reminderDate or ""

    def get_reminder_time(self) -> str:
        return self.reminder_time or self.reminderTime or ""


class CalendarEventCreate(CalendarEventBase):
    declaration_id: Optional[int] = None


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    reference_code: Optional[str] = None
    referenceCode: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[str] = None
    eventDate: Optional[str] = None
    date: Optional[str] = None
    time_slot: Optional[str] = None
    timeSlot: Optional[str] = None
    time: Optional[str] = None
    reminder_date: Optional[str] = None
    reminderDate: Optional[str] = None
    reminder_time: Optional[str] = None
    reminderTime: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    declaration_id: Optional[int] = None


class CalendarEventResponse(BaseModel):
    id: int
    user_id: int
    declaration_id: Optional[int] = None
    title: str
    category: str
    reference_code: Optional[str] = None
    referenceCode: Optional[str] = None
    location: str
    event_date: str
    eventDate: Optional[str] = None
    date: Optional[str] = None
    time_slot: str
    timeSlot: Optional[str] = None
    time: Optional[str] = None
    reminder_date: Optional[str] = None
    reminderDate: Optional[str] = None
    reminder_time: Optional[str] = None
    reminderTime: Optional[str] = None
    description: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_custom(cls, obj) -> "CalendarEventResponse":
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            declaration_id=obj.declaration_id,
            title=obj.title,
            category=obj.category,
            reference_code=obj.reference_code,
            referenceCode=obj.reference_code,
            location=obj.location,
            event_date=obj.event_date,
            eventDate=obj.event_date,
            date=obj.event_date,
            time_slot=obj.time_slot,
            timeSlot=obj.time_slot,
            time=obj.time_slot,
            reminder_date=obj.reminder_date,
            reminderDate=obj.reminder_date,
            reminder_time=obj.reminder_time,
            reminderTime=obj.reminder_time,
            description=obj.description,
            status=obj.status,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
