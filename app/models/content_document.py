from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, func
from app.core.database import Base


class ContentDocument(Base):
    """Legal & Information Content Documents (Privacy Policy, Terms, About Us)."""
    __tablename__ = "content_documents"

    id = Column(String(50), primary_key=True, index=True)
    type = Column(String(50), unique=True, index=True, nullable=False)  # privacy-policy, about-us, terms-and-condition
    title = Column(String(255), nullable=False)
    card_title = Column(String(255), nullable=False)
    hero_title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    paragraphs = Column(JSON, nullable=False, default=list)
    last_updated = Column(String(50), nullable=True)
    is_published = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
