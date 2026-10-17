from sqlalchemy import Column, String, Text, DateTime, func
from app.core.database import Base


class IncorrectDataReport(Base):
    """Signalement d'anomalies et données incorrectes (Discrepancy Reports)."""
    __tablename__ = "incorrect_data_reports"

    id = Column(String(50), primary_key=True, index=True)
    report_code = Column(String(50), unique=True, index=True, nullable=False)
    reporting_user = Column(String(150), nullable=False, default="Utilisateur DGDA")
    email = Column(String(150), nullable=True, default="")
    telephone = Column(String(100), nullable=True, default="")
    description = Column(String(255), nullable=False, default="Signalement de discordance")
    detailed_description = Column(Text, nullable=False)
    status = Column(String(20), default="PENDING", index=True)  # PENDING, UNDER_REVIEW, RESOLVED
    admin_notes = Column(Text, nullable=True)
    submission_date = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
