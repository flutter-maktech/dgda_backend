from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class CustomsDocument(Base):
    __tablename__ = "customs_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, default="Procedures & Forms", index=True)
    format = Column(String(20), nullable=False, default="PDF")
    file_size = Column(String(50), nullable=False, default="2.4 MB")
    date = Column(String(50), nullable=False, default="Août 2024")
    download_url = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
