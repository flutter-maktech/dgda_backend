from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class EventCategory(str, enum.Enum):
    FORWARDER_MEETING = "Forwarder Meeting"
    PHYSICAL_INSPECTION = "Physical Inspection"
    VALUATION_CLEARANCE = "Valuation Clearance"
    CUSTOMS_AUDIT = "Customs Audit"
    DOCUMENT_VERIFICATION = "Document Verification"


class EventStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    declaration_id = Column(Integer, ForeignKey("declarations.id", ondelete="SET NULL"), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    category = Column(String(100), default="Forwarder Meeting", nullable=False)
    reference_code = Column(String(100), nullable=True)
    location = Column(String(255), default="Matadi Port Customs Office", nullable=False)
    event_date = Column(String(50), nullable=False, index=True)
    time_slot = Column(String(50), default="10:00 AM", nullable=False)
    reminder_date = Column(String(50), nullable=True)
    reminder_time = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="scheduled", nullable=False, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", backref="calendar_events")
    declaration = relationship("Declaration", backref="calendar_events")

    def __repr__(self) -> str:
        return f"<CalendarEvent(id={self.id}, title='{self.title}', date='{self.event_date}', status='{self.status}')>"
