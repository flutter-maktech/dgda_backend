from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from app.core.database import Base


class BookmarkType(str, enum.Enum):
    NEWS = "news"
    DOCUMENT = "document"
    OFFICE = "office"


class UserBookmark(Base):
    __tablename__ = "user_bookmarks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(String(50), nullable=False, index=True)  # "news", "document", "office"
    item_id = Column(String(100), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "item_type", "item_id", name="uq_user_item_bookmark"),
    )

    def __repr__(self) -> str:
        return f"<UserBookmark(user_id={self.user_id}, type={self.item_type}, item_id={self.item_id})>"
