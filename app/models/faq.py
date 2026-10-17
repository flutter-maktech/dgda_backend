from sqlalchemy import Column, String, Text, Integer, DateTime, func
from app.core.database import Base


class FAQ(Base):
    """Foire Aux Questions (FAQ) Model for DGDA."""
    __tablename__ = "faqs"

    id = Column(String(50), primary_key=True, index=True)
    no = Column(Integer, default=1, index=True)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, INACTIVE
    category = Column(String(100), default="General", index=True)  # General, Douane, Sydonia, etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
