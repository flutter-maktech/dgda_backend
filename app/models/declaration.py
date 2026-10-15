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


class DeclarationStatus(str, enum.Enum):
    ALL = "all"
    PENDING = "pending"
    IN_PROGRESS = "inProgress"
    VALIDATED = "validated"
    REJECTED = "rejected"


class Declaration(Base):
    __tablename__ = "declarations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_code = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)  # Import, Export, Transit T1 SADC, Temporary Admission
    location = Column(String(150), nullable=False)  # Matadi Port, Kinshasa Main Office, Kasumbalesa, etc.
    status = Column(String(50), default="pending", nullable=False, index=True)
    hs_code = Column(String(50), nullable=True)
    container_teu = Column(String(50), nullable=True)
    estimated_duty_usd = Column(String(50), nullable=True)
    good_description = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship("User", backref="declarations")

    def __repr__(self) -> str:
        return f"<Declaration(id={self.id}, ref='{self.reference_code}', status='{self.status}')>"
