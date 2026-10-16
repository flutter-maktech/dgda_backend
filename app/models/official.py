from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, func, JSON
from app.core.database import Base


class GovernmentOfficial(Base):
    """Présidence & Gouvernement Official Model."""
    __tablename__ = "government_officials"

    id = Column(String, primary_key=True, index=True)
    badge_text = Column(String, nullable=False)
    role_title = Column(String, nullable=False)
    honorific = Column(String, nullable=False)
    name = Column(String, nullable=False)
    photo_path = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    biography = Column(Text, nullable=False)
    responsibilities = Column(JSON, nullable=False, default=list)
    mandate_period = Column(String, nullable=False)
    cabinet_office = Column(String, nullable=True)
    official_website = Column(String, nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ManagementMember(Base):
    """DGDA Direction & Responsables Model."""
    __tablename__ = "management_members"

    id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    role_or_title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)
    quote = Column(Text, nullable=True)
    asset_path = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    source_reference = Column(String, nullable=True)
    official_email = Column(String, nullable=True, default="contact@douane.gouv.cd")
    official_phone = Column(String, nullable=True, default="+243 82 192 0215")
    official_source_url = Column(String, nullable=True, default="https://douane.gouv.cd/dgda/services/")
    category = Column(String, nullable=False, index=True)  # directionGenerale, directeursCentraux, directeursProvinciaux, representantsEtranger, delegationSyndicale
    filter_tag = Column(String, nullable=True)
    is_dg = Column(Boolean, default=False)
    is_dga = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
