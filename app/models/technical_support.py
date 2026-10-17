from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, func
from app.core.database import Base


class TechnicalSupportInfo(Base):
    """Configuration et coordonnées de l'Assistance Technique / Helpdesk 24/7 DGDA."""
    __tablename__ = "technical_support_info"

    id = Column(String(50), primary_key=True, index=True, default="dgda-helpdesk")
    title = Column(String(255), nullable=False, default="Assistance DGDA 24h/24 et 7j/7")
    description = Column(Text, nullable=False)
    phone_numbers = Column(String(255), nullable=False, default="+243 81 700 0001 / +243 99 800 0002")
    phone_list = Column(JSON, nullable=False, default=list)
    email = Column(String(150), nullable=False, default="support.sydonia@dgda.gouv.cd")
    whatsapp = Column(String(50), nullable=True, default="+243 82 192 0215")
    portal_url = Column(String(255), nullable=True, default="https://douane.gouv.cd/assistance")
    operating_hours = Column(String(100), nullable=False, default="24/7 - Service Continu")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SupportTicket(Base):
    """Tickets d'assistance technique soumis par les déclarants et usagers."""
    __tablename__ = "support_tickets"

    id = Column(String(50), primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(100), nullable=True)
    subject = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, default="SydoniaWorld")  # SydoniaWorld, Scellé, Quittance, Autre
    message = Column(Text, nullable=False)
    status = Column(String(20), default="OPEN", index=True)  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(20), default="NORMAL")  # NORMAL, HIGH, URGENT
    admin_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
