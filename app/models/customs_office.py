from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class CustomsOffice(Base):
    __tablename__ = "customs_offices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), nullable=False, default="[CDMAT]")
    name = Column(String(255), nullable=False, index=True)
    subtitle = Column(String(255), nullable=False, default="Primary Maritime Port")
    office_location = Column(String(255), nullable=False)
    working_hours = Column(String(100), nullable=False, default="24/7 Commercial Corridors")
    station_code = Column(String(100), nullable=False, default="CD-STN-421")
    region = Column(String(100), nullable=False, default="Kongo Central", index=True)
    authority = Column(String(100), nullable=False, default="Inspecteur Principal")
    juxtaposed_post = Column(String(255), nullable=True)
    tags = Column(String(500), nullable=False, default="Import,Export,Transit,Maritime Port")
    phone = Column(String(50), nullable=False, default="+243 81 234 5678")
    is_open = Column(Boolean, nullable=False, default=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
