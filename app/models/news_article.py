from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    subtitle = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    date = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    image_url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
