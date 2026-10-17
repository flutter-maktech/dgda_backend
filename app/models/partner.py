from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, func, JSON
from app.core.database import Base


class Partner(Base):
    """Partner, Sponsor, or Recommended Professional Model."""
    __tablename__ = "partners"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=False, default="Partners", index=True)  # Partners, Sponsors, Logistics, Banking, Insurance, etc.
    tier = Column(String(100), nullable=False, default="Official Partner")  # Principal Sponsor, Official Partner, Recommended Professional, etc.
    is_principal_sponsor = Column(Boolean, default=False, index=True)
    is_partner = Column(Boolean, default=True, index=True)  # True = Partner/Sponsor, False = Recommended Professional
    status = Column(String(20), default="Active", index=True)  # Active, Inactive

    logo_url = Column(String(500), nullable=True)
    asset_path = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    address = Column(String(255), nullable=True)

    role = Column(String(150), nullable=True)
    tagline = Column(String(255), nullable=True)
    headline = Column(String(255), nullable=True)
    hero_subtitle = Column(Text, nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    about_text = Column(Text, nullable=True)
    services = Column(JSON, nullable=False, default=list)
    slogan = Column(String(255), nullable=True)

    is_official_badge = Column(Boolean, default=True)
    is_trusted_badge = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
