from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from app.core.database import Base


class UserNotificationRead(Base):
    __tablename__ = "user_notification_reads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_id = Column(String(50), ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    read_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "notification_id", name="uq_user_notification_read"),
    )

    def __repr__(self) -> str:
        return f"<UserNotificationRead(user_id={self.user_id}, notification_id={self.notification_id})>"
