from sqlalchemy import Column, String, Text, DateTime, func
from app.core.database import Base


class Notification(Base):
    """Notification Push et Alertes Opérationnelles pour la DGDA."""
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    target_audience = Column(String(100), default="All Users", index=True)  # All Users, Importers, Exporters, Customs Brokers
    category = Column(String(100), default="Operational Alert", index=True)  # Operational Alert, System Maintenance, Regulatory Update, Urgent Bulletin
    priority = Column(String(100), default="Normal Priority")  # High Priority (Immediate Ingress), Normal Priority, Low / Informational
    sent_at = Column(String(100), nullable=True)
    audience_reach = Column(String(50), default="Tous les usagers")
    open_rate = Column(String(20), default="0%")
    status = Column(String(30), default="delivered", index=True)  # delivered, broadcasting, scheduled

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
